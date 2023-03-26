#!/bin/bash

if [[ "$#" -ne 3 ]]; then
	echo "USAGE: $0 MATRIX INCLUDE EXCLUDE"
	exit 1
fi

# Replace all spaces including newlines with whitespaces.
INPUT_MATRIX="${1//[[:space:]]/ }"
INPUT_INCLUDE="${2//[[:space:]]/ }"
INPUT_EXCLUDE="${3//[[:space:]]/ }"

MATRIX="{}"
# Define REGEX patterns for grep.
RE_WORD='[^\s:,]+'
RE_VARIABLE="(?<=^|,)\s*${RE_WORD}\s*:(\s*${RE_WORD})+\s*(?=,|$)"
# Check if the *whole* matrix consists only of spaces.
if [[ -z "${INPUT_MATRIX//[[:space:]]/}" ]]; then
	echo "'matrix' input is empty or not set. Skip matrix section."
else
	# Check if the *whole* matrix consists of variables divided by commas.
	if echo "$INPUT_MATRIX" | grep -qoP "^(${RE_VARIABLE},)*${RE_VARIABLE},?\s*$"; then
		VARIABLES="$(echo "$INPUT_MATRIX" | grep -oP "$RE_VARIABLE" | jq -R 'capture("^\\s*(?<key>[^\\s:,]+)\\s*:(?<value>.*)$") | .value |= [ scan("[^\\s:,]+") ] | [.] | from_entries')"
		# shellcheck disable=SC2207
		DUPLICATED_VARIABLES=($(echo "$VARIABLES" | jq 'keys' | jq -s 'add' | jq -r 'group_by(.) | map(select(length>1) | .[0]) | .[]'))
		if [[ "${#DUPLICATED_VARIABLES[@]}" -eq 0 ]]; then
			MATRIX="$(echo "${MATRIX}${VARIABLES}" | jq -s 'add')"
		else
			echo "Duplicated variable names in matrix are forbidden by GitHub, but following duplicated names found:"
			printf '%s\n' "${DUPLICATED_VARIABLES[@]}"
			exit 1
		fi
	else
		PRINT_ROW="\tkey: value value <...> value,\n"
		# shellcheck disable=SC2059
		printf "Matrix should fulfill the following pattern:\n\n${PRINT_ROW}${PRINT_ROW}\t<...>\n${PRINT_ROW}\nwith unique keys, but 'matrix' input with the following pattern received:\n\n"
		# shellcheck disable=SC2207
		IFS=',' CHECK_MATRIX_ROWS=($(echo "$INPUT_MATRIX" | sed 's/[^[:space:]:,]\+/value/g; s/[^[:space:]:,]\+[[:space:]]*:/key:/g; s/[[:space:]]*,[[:space:]]*/,/g; s/[[:space:]]\+/ /g; s/^[[:space:]]*//g; s/[[:space:]]*$//g;'))
		printf '\t%s,\n' "${CHECK_MATRIX_ROWS[@]}"
		exit 1
	fi
fi

if [[ -z "${INPUT_INCLUDE//[[:space:]]/}" ]]; then
	echo "'include' input is empty or not set. Skip include section."
else
	:
fi

if [[ -z "${INPUT_EXCLUDE//[[:space:]]/}" ]]; then
	echo "'exclude' input is empty or not set. Skip exclude section."
else
	:
fi
