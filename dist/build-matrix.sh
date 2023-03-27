#!/bin/bash

HELP="Usage: $0 MATRIX INCLUDE EXCLUDE

Parse a matrix for GiHub jobs in JSON format from the given arguments."

if [[ "$#" -ne 3 ]]; then
	echo "Exactly 3 arguments expected, but $# arguments received." >&2
	echo "$HELP" >&2
	exit 1
fi

# Replace all spaces including newlines with whitespaces.
INPUT_MATRIX="${1//[[:space:]]/ }"
declare -A INPUT_EXTRAS=([include]="${2//[[:space:]]/ }" [exclude]="${3//[[:space:]]/ }")
MATRIX="{}"

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
		DUPLICATED_VARIABLES=($(echo "$VARIABLES" | jq 'keys' | jq -s 'add' | jq -r 'group_by(.) | map(select(length>1) | .[0]) | .[]'))
		if [[ "${#DUPLICATED_VARIABLES[@]}" -eq 0 ]]; then
			MATRIX="$(echo "${MATRIX}${VARIABLES}" | jq -s 'add')"
		else
			echo "Duplicated variable names in matrix are forbidden, but following duplicated names found:" >&2
			printf '%s\n' "${DUPLICATED_VARIABLES[@]}" >&2
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
	echo "$EXTRA_NAME"
	INPUT_EXTRA="${INPUT_EXTRAS[$EXTRA_NAME]}"
	# Check if extra consists not only of spaces.
	if [[ -n "${INPUT_EXTRA//[[:space:]]/}" ]]; then
		if echo "$INPUT_EXTRA" | grep -qoP "^(${RE_COMBINATION},)*${RE_COMBINATION},?\s*$"; then
			echo "$INPUT_EXTRA" | grep -oP "$RE_COMBINATION"
			# | jq -R 'capture("^\\s*(?<key>[^\\s:,]+)\\s*:(?<value>.*)$") | .value |= [ scan("[^\\s:,]+") ] | [.] | from_entries')"
		else
			echo "${EXTRA_NAME^^} with invalid syntax received." >&2
			echo "$HELP" >&2
			exit 1
		fi
	else
		echo "'${EXTRA_NAME^^}' argument is empty or not set. Skip ${EXTRA_NAME} section."
	fi
done
