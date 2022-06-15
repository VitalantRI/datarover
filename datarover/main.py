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

from . import db
from . import security
from . import create_app
app = create_app()

if __name__ == "__main__":
    # for testing only
    app.run(host="0.0.0.0", debug=True, port=80)
