#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

echo "Debug: ${INPUT_version} | ${INPUT_output_file} | \
${INPUT_output_folder} | ${INPUT_input_folder} | \
${INPUT_base_path} | ${INPUT_cdn}"

# Ensure required envs are set
: ${INPUT_version:?}
: ${INPUT_output_file:?}
: ${INPUT_output_folder:?}
: ${INPUT_input_folder:?}
: ${INPUT_base_path:?}
: ${INPUT_cdn:?}

OutputDir=$(pwd)/${INPUT_output_folder:-.}
InputDir=$(pwd)/${INPUT_input_folder:-.}

echo "#################################"
echo "#        Building Manifest      #"
echo "#################################"

echo "Exporting to: ${OutputDir}"
echo "Exporting as: ${output_file}"
echo "Generating for Folder: ${InputDir}"

python /root/manifest_creator.py --t 4 --output_folder $OutputDir \
 --directory ${InputDir} --export ${INPUT_output_file} --build ${INPUT_version} \
 --cdn ${INPUT_cdn} --base_path ${INPUT_base_path}