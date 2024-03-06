#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Ensure required envs are set
: ${version:?}
: ${output_file:?}
: ${output_folder:?}
: ${input_folder:?}

OutputDir=${output_folder:-.}

echo "#################################"
echo "#        Building Manifest      #"
echo "#################################"

echo "Exporting to: ${OutputDir}"
echo "Exporting as: ${output_file}"

python /root/manifest_creator.py --t 3 --output_folder $OutputDir  --dir ${input_folder} --export ${output_file} --build ${version}