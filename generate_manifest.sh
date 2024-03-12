#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Function to get variable value; prefers INPUT_ prefixed version if set
get_var() {
    local input_var="INPUT_$1"
    local non_input_var="$1"
    if [ ! -z "${!input_var:-}" ]; then
        echo "${!input_var}"
    else
        echo "${!non_input_var:-}"
    fi
}

version=$(get_var "version")
output_file=$(get_var "output_file")
output_folder=$(get_var "output_folder")
input_folder=$(get_var "input_folder")
base_path=$(get_var "base_path")
cdn=$(get_var "cdn")

# echo "Debug: ${version} | ${output_file} | ${output_folder} | ${input_folder} | ${base_path} | ${cdn}"

# Ensure required envs are set
: ${version:?}
: ${output_file:?}
: ${output_folder:?}
: ${input_folder:?}
: ${base_path:?}
: ${cdn:?}

OutputDir=$(pwd)/${output_folder:-.}
InputDir=$(pwd)/${input_folder:-.}

echo "#################################"
echo "#        Building Manifest      #"
echo "#################################"

echo "Exporting to: ${OutputDir}"
echo "Exporting as: ${output_file}"
echo "Generating for Folder: ${InputDir}"

python /root/manifest_creator.py --t 4 --output_folder $OutputDir \
 --directory ${InputDir} --export ${output_file} --build ${version} \
 --cdn ${cdn} --base_path ${base_path}
