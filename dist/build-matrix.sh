#!/bin/bash
set -e

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
All names and values of variables must not contain any spaces, colons and commas. Any spaces can be used for word and line separation."

function fail {
	# Print error message if given, print help and exit with code 1.
	echo "Error${1:+: $1}" >&2
	echo >&2
	echo "$HELP" >&2
	exit 1
}

fail

function sanitize {
	# Sanitize string as expected in further steps:
	# - replace all spaces (including newlines) with simple whitespaces;
	# - remove trailing comma;
	# - replace all other commas with newlines (i.e. split string by commas).
	if [[ "$#" -ne 1 ]]; then
		echo "Error: Single argument to sanitize expected, but $# arguments received." >&2
		exit 1
	fi
	echo "${1//[[:space:]]/ }" | sed 's/,\s*$//g' | sed 's/,/\n/g'
}

if [[ "$#" -ne 3 ]]; then
	fail "Exactly 3 arguments expected, but $# arguments received."
fi

INPUT_MATRIX="$1"
declare -A INPUT_EXTRAS=([include]="$2" [exclude]="$3")
MATRIX=""

# Define REGEX patterns for grep.
RE_WORD='[^\s:,]+'
RE_VARIABLE="${RE_WORD}\s*:(\s*${RE_WORD})+"
RE_COMBINATION="(${RE_WORD}\s*:\s*${RE_WORD}\s*)+"

# Check if the whole matrix consists not only of spaces.
if [[ -n "${INPUT_MATRIX//[[:space:]]/}" ]]; then
	INPUT_MATRIX="$(sanitize "$INPUT_MATRIX")"
	# Check if every row filfills the expected pattern.
	if echo "$INPUT_MATRIX" | grep -qvP "^\s*${RE_VARIABLE}\s*$"; then
		ERROR_MESSAGE="$(
			echo "Invalid matrix rows found:"
			echo "$INPUT_MATRIX" | grep -vP "^\s*${RE_VARIABLE}\s*$" |
				sed 's/^\s*\|\s*$/\t/g;'
		)"
		fail "$ERROR_MESSAGE"
		# INVALID_ROWS="$(echo "$INPUT_MATRIX" | grep -vP "^\s*${RE_VARIABLE}\s*$" \
		# 	| sed 's/^\s*\|\s*$//g;' | jq -R | jq -rs 'join(", ")')"
		# fail "Invalid matrix rows found: ${INVALID_ROWS}."
	fi
	VARIABLES="$(echo "$INPUT_MATRIX" | grep -oP "$RE_VARIABLE" |
		jq -R 'capture("^\\s*(?<key>[^\\s:,]+)\\s*:(?<value>.*)$") | .value |= [scan("[^\\s:,]+")] | [.] | from_entries')"
	# Check for duplicates in variable names.
	DUPLICATES="$(echo "$VARIABLES" | jq 'keys' |
		jq -rs 'add | group_by(.) | map(select(length>1) | .[0]) | join(", ")')"
	if [[ -n "$DUPLICATES" ]]; then
		fail "Following duplicated variable names found in matrix: ${DUPLICATES}."
	fi
	# Check for invalid variable names.
	RESERVED_NAMES="$(echo "$VARIABLES" | jq 'keys' |
		jq -rs 'add | map(select(test("^(include|exclude)$"))) | join(", ")')"
	if [[ -n "$RESERVED_NAMES" ]]; then
		fail "Following reserved variable names found in matrix: ${RESERVED_NAMES}."
	fi
	MATRIX="$(echo "${MATRIX}${VARIABLES}" | jq -s 'add')"
fi

for EXTRA_NAME in "${!INPUT_EXTRAS[@]}"; do
	INPUT_EXTRA="${INPUT_EXTRAS[$EXTRA_NAME]}"
	# Check if extra consists not only of spaces.
	if [[ -n "${INPUT_EXTRA//[[:space:]]/}" ]]; then
		INPUT_EXTRA="$(sanitize "$INPUT_EXTRA")"

		# Check if every combination filfills the expected pattern.
		if echo "$INPUT_EXTRA" | grep -qvP "^\s*${RE_COMBINATION}\s*$"; then
			ERROR_MESSAGE="$(
				echo "Invalid combinations found in ${EXTRA_NAME}:"
				echo "$INPUT_EXTRA" | grep -vP "^\s*${RE_COMBINATION}\s*$" |
					sed 's/^\s*\|\s*$/\t/g;'
			)"
			fail "$ERROR_MESSAGE"
		fi
		EXTRA="$(echo "$INPUT_EXTRA" | grep -oP "$RE_COMBINATION" |
			jq -R '[capture("(?<key>[^\\s:,]+)\\s*:\\s*(?<value>[^\\s:,]+)"; "g")]')"
		DUPLICATES="$(echo "$EXTRA" | jq 'group_by(.key) | map(select(length>1) | .[0].key)')"
		if [[ "$(echo "$DUPLICATES" | jq -s 'map(length) | add')" -ne 0 ]]; then
			ERROR_MESSAGE="$(
				echo "Duplicated variable names found in ${EXTRA_NAME}:"
				echo "$DUPLICATES" | jq -rs 'map(join(", ")) | to_entries | map(select(.value != "")) | map("Combination " + (.key | tostring) + ": " + .value) | .[]'
			)"
			fail "$ERROR_MESSAGE"
		fi
		EXTRA="$(echo "$EXTRA" | jq 'from_entries' | jq -s "{$EXTRA_NAME: .}")"
		MATRIX="$(echo "${MATRIX}${EXTRA}" | jq -s 'add')"
	fi
done

if [[ -z "$MATRIX" ]]; then
	fail "At least one of matrix, include or exclude should be not empty"
fi

echo "$MATRIX"
