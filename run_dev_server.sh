# Data Rover
# Copyright (C) 2022  Vitalant
# Developed by Vincent Chiang

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#!/bin/sh
# if [ -z "$1" ]
# then
#       echo "No config file provided, using config.json"
#       cp config.json appdata/config.json
# else
#       echo "Using $1"
#       cp $1 datarover/config.json
# fi
source ./env/bin/activate
pip install -e .
export FLASK_APP=datarover
export FLASK_ENV=development
python -m flask run