#!/bin/bash

HELP="Usage: $0 MATRIX INCLUDE EXCLUDE

Parse a matrix for GitHub jobs in JSON format from the given arguments.

MATRIX arguments should fulfill the following pattern with unique variable names different from the reserved 'include' and 'exclude':
	variable-1: value value ...,
	variable-2: value value ...,
	             ...
	variable-n: value value ...[,]
INCLUDE and EXCLUDE arguments should fulfill the followind pattern with unique variable names inside each combination:
	variable-i: value variable-j: value ...,
	                   ...
	variable-k: value variable-l: value ...[,]
All variables' names and values must not contain any spaces, colons and commas. Any spaces can be used for word and line separation."

if [[ "$#" -ne 3 ]]; then
	echo "Exactly 3 arguments expected, but $# arguments received." >&2
	echo "$HELP" >&2
	exit 1
fi

# Replace all spaces including newlines with whitespaces.
INPUT_MATRIX="${1//[[:space:]]/ }"
declare -A INPUT_EXTRAS=([include]="${2//[[:space:]]/ }" [exclude]="${3//[[:space:]]/ }")
MATRIX=""

# Define REGEX patterns for grep.
RE_WORD='[^\s:,]+'
RE_VARIABLE="(?<=^|,)\s*${RE_WORD}\s*:(\s*${RE_WORD})+\s*(?=,|$)"
RE_COMBINATION="(?<=^|,)(\s*${RE_WORD}\s*:\s*${RE_WORD}\s*)+(?=,|$)"

# Check if the whole matrix consists not only of spaces.
if [[ -n "${INPUT_MATRIX//[[:space:]]/}" ]]; then
	# Check if the whole matrix consists of variables divided by commas.
	if echo "$INPUT_MATRIX" | grep -qoP "^(${RE_VARIABLE},)*${RE_VARIABLE},?\s*$"; then
		VARIABLES="$(echo "$INPUT_MATRIX" | grep -oP "$RE_VARIABLE" | jq -R 'capture("^\\s*(?<key>[^\\s:,]+)\\s*:(?<value>.*)$") | .value |= [ scan("[^\\s:,]+") ] | [.] | from_entries')"
		# shellcheck disable=SC2207
		DUPLICATES_ARRAY=($(echo "$VARIABLES" | jq 'keys' | jq -s 'add' | jq -r 'group_by(.) | map(select(length>1) | .[0]) | .[]'))
		if [[ "${#DUPLICATES_ARRAY[@]}" -eq 0 ]]; then
			MATRIX="$(echo "${MATRIX}${VARIABLES}" | jq -s 'add')"
		else
			echo "Duplicated variable names in matrix are forbidden, but following duplicated names found:" >&2
			printf '%s\n' "${DUPLICATES_ARRAY[@]}" >&2
			exit 1
		fi
	else
		PRINT_ROW="\tkey: value value <...> value,\n"
		# shellcheck disable=SC2059
		printf "Matrix should fulfill the following pattern:\n\n${PRINT_ROW}${PRINT_ROW}\t<...>\n${PRINT_ROW}\nwith unique keys, but 'matrix' input with the following pattern received:\n\n" >&2
		# shellcheck disable=SC2207
		IFS=',' CHECK_MATRIX_ROWS=($(echo "$INPUT_MATRIX" | sed 's/[^[:space:]:,]\+/value/g; s/[^[:space:]:,]\+[[:space:]]*:/key:/g; s/[[:space:]]*,[[:space:]]*/,/g; s/[[:space:]]\+/ /g; s/^[[:space:]]*//g; s/[[:space:]]*$//g;'))
		printf '\t%s,\n' "${CHECK_MATRIX_ROWS[@]}" >&2
		exit 1
	fi
fi

for EXTRA_NAME in "${!INPUT_EXTRAS[@]}"; do
	INPUT_EXTRA="${INPUT_EXTRAS[$EXTRA_NAME]}"
	# Check if extra consists not only of spaces.
	if [[ -n "${INPUT_EXTRA//[[:space:]]/}" ]]; then
		if echo "$INPUT_EXTRA" | grep -qoP "^(${RE_COMBINATION},)*${RE_COMBINATION},?\s*$"; then
			EXTRA="$(echo "$INPUT_EXTRA" | grep -oP "$RE_COMBINATION" |
				jq -R '[capture("(?<key>[^\\s:,]+)\\s*:\\s*(?<value>[^\\s:,]+)"; "g")]')"
			DUPLICATES="$(echo "$EXTRA" | jq 'group_by(.key) | map(select(length>1) | .[0].key)')"
			if [[ "$(echo "$DUPLICATES" | jq -s 'map(length) | add')" -eq 0 ]]; then
				EXTRA="$(echo "$EXTRA" | jq 'from_entries' | jq -s "{$EXTRA_NAME: .}")"
				MATRIX="$(echo "${MATRIX}${EXTRA}" | jq -s 'add')"
			else
				IFS=':' read -r -a DUPLICATES_ARRAY <<<"$(echo "$DUPLICATES" | jq -rs 'map(join(", ")) | join(":")')"
				ERROR_STRINGS=("Duplicated variable names found in ${EXTRA_NAME^^}:")
				for I in "${!DUPLICATES_ARRAY[@]}"; do
					DUPLICATE="${DUPLICATES_ARRAY[$I]}"
					if [[ -n "${DUPLICATE//[[:space:]]/}" ]]; then
						ERROR_STRINGS+=("Combination ${I}: ${DUPLICATE}")
					fi
				done
				printf '%s\n' "${ERROR_STRINGS[@]}" >&2
				echo "$HELP" >&2
				exit 1
			fi
		else
			echo "${EXTRA_NAME^^} with invalid syntax received." >&2
			echo "$HELP" >&2
			exit 1
		fi
	fi
done

if [[ -z "$MATRIX" ]]; then
	echo "At least one of matrix, include or exclude should be not empty, but all 3 empty arguments received." >&2
	echo "$HELP" >&2
	exit 1
fi

echo "$MATRIX"
