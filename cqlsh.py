#!/bin/sh
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# shell script to find a suitable Python interpreter and run cqlsh.py

# Use the Python that is specified in the env
if [ -n "$CQLSH_PYTHON" ]; then
    USER_SPECIFIED_PYTHON="$CQLSH_PYTHON"
fi


# filter "--python" option and its value, and keep remaining arguments as it is
USER_SPECIFIED_PYTHON_OPTION=false
for arg do
  shift
  case "$arg" in
    --python)
        USER_SPECIFIED_PYTHON_OPTION=true
        ;;
    --)
        break
        ;;
    *)
        if [ "$USER_SPECIFIED_PYTHON_OPTION" = true ] ; then
            USER_SPECIFIED_PYTHON_OPTION=false
            USER_SPECIFIED_PYTHON="$arg"
        else
            set -- "$@" "$arg"
        fi
        ;;
  esac
done

if [ "$USER_SPECIFIED_PYTHON_OPTION" = true ] ; then
    echo "You must specify a python interpreter path with the --python option"
    exit 1
fi

# get a version string for a Python interpreter
get_python_version() {
    interpreter=$1
    version=$($interpreter -c "import os; print('{}.{}'.format(os.sys.version_info.major, os.sys.version_info.minor))" 2> /dev/null)
    echo "$version"
}

# test whether a version string matches one of the supported versions for cqlsh
is_supported_version() {
    version=$1
    major_version="${version%.*}"
    minor_version="${version#*.}"
    # python 3.8-3.11 are supported
    if [ "$major_version" = 3 ] && [ "$minor_version" -ge 8 ] && [ "$minor_version" -le 11 ]; then
        echo "supported"
    # python 3.6-3.7 are deprecated
    elif [ "$major_version" = 3 ] && [ "$minor_version" -ge 6 ] && [ "$minor_version" -le 7 ]; then
        echo "deprecated"
    else
        echo "unsupported"
    fi
}

run_if_supported_version() {
    # get the interpreter and remove it from argument
    interpreter="$1" shift

    version=$(get_python_version "$interpreter")
    version_status=$(is_supported_version "$version")
    if [ -n "$version" ]; then
        if [ "$version_status" = "supported" ] || [ "$version_status" = "deprecated" ]; then
            if [ "$version_status" = "deprecated" ]; then
                echo "Warning: using deprecated version of Python:" "$version" >&2
            fi

            exec "$interpreter" "$($interpreter -c "import os; print(os.path.dirname(os.path.realpath('$0')))")/cqlsh.py" "$@"
            exit
        else
            echo "Warning: unsupported version of Python, required 3.6-3.11 but found" "$version" >&2
        fi
    fi
}


if [ "$USER_SPECIFIED_PYTHON" != "" ]; then
    # run a user specified Python interpreter
    run_if_supported_version "$USER_SPECIFIED_PYTHON" "$@"
else
    for interpreter in python3 python; do
        run_if_supported_version "$interpreter" "$@"
    done
fi

echo "No appropriate Python interpreter found." >&2
exit 1
