Selected Files Directory Structure:

└── ./
    └── signoff-dsc-runscript
        ├── input_config.yaml.md
        ├── netlist_preprocessing.py.md
        ├── pre_setting.py.md
        ├── run.sh.md
        ├── run.tcl.md
        └── signoff-dsc-runscript.md



--- signoff-dsc-runscript/netlist_preprocessing.py.md ---


```python

import re
import os
import argparse
from collections import defaultdict


class NetlistPreprocessing:
    def __init__(self):
        self.instance_pattern = ["x", "r", "c", "q", "d", "m"]

    def _transform_line(self, line):
        """주어진 줄을 특정 문법으로 변환"""
        return line.replace(" / ", " ").replace(" ( ", " ").replace(" ) ", " ").replace(" )\n", "\n").replace("[", "<").replace("]", ">").replace("!", "_").replace("(", "_").replace(")", "_").replace("|", "_").replace("#", "_").replace("\\", "_")

    def _edit_and_merge(self, file_path, merged_lines, visited_files=None):
        if visited_files is None:
            visited_files = set()
        if file_path in visited_files:
            return
        visited_files.add(file_path)

        with open(file_path, "r") as infile:
            print(f"Processing: {file_path}")
            is_param = False
            merged_lines.append(f"* {file_path}")
            for line in infile:
                line = re.sub(r"\s+", " ", line.strip())
                # if not line or line.startswith(("*", "$", "#")):
                if not line:
                    continue

                if line.lower()[0] in self.instance_pattern:
                    new_line = []
                    for word in line.split():
                        if "=" not in word:
                            new_line.append(word.replace("/", "."))
                        else:
                            new_line.append(word)
                    line = " ".join(new_line)

                if line.lower().startswith(".param"):
                    is_param = True
                elif is_param and not line.startswith("+"):
                    is_param = False

                if line.startswith("+"):
                    previous = merged_lines.pop().rstrip("\n")
                    transformed_line = self._transform_line(line[1:]) if not is_param else line[1:]
                    merged_lines.append(previous + transformed_line + "\n")
                    continue

                if line.lower().startswith((".inc", ".include")):
                    if ".star" in line.lower():
                        print("# Warning: change star to spc netlist file")
                    included_file = line.split(" ", 1)[1].strip().strip("'").strip('"')
                    if os.path.isfile(included_file):
                        self._edit_and_merge(included_file, merged_lines, visited_files)
                    else:
                        print(f"# Warning: File not found: {included_file}")
                else:
                    transformed_line = self._transform_line(line)
                    if transformed_line.strip():
                        merged_lines.append(transformed_line + "\n")
            merged_lines.append("\n")

    def _include_netlist_files(self, netlist_entries):
        merged_lines = []
        for entry in netlist_entries:
            if not entry.strip() or entry.startswith(("*", "$", "#")):
                continue
            try:
                # file_path = entry.split(" ", 1)[1].strip().strip("'")
                file_path = entry.strip().split(" ", 1)[1].strip("'").strip('"')
            except IndexError:
                continue
            if os.path.isfile(file_path):
                self._edit_and_merge(file_path, merged_lines)
            else:
                print(f"# Warning: File not found: {file_path}")
        return merged_lines

    def _parse_netlist(self, netlist_lines):
        subckt_definitions = {}
        subckt_calls = []
        current_subckt = None
        subckt_lines = []
        etc_lines = []    # comments, ...

        for line in netlist_lines:
            line = line.strip()
            line_lower = line.lower()
            if not line_lower:
                continue
            elif line_lower.startswith(".subckt"):
                current_subckt = line.split()[1].strip()
                if current_subckt in subckt_definitions.keys():
                    print(f"# Warning: Overwriting subckt definitions: {current_subckt}")
                subckt_lines = [line]
            elif line_lower.startswith(".ends") and current_subckt:
                subckt_lines.append(line)
                subckt_definitions[current_subckt] = subckt_lines
                current_subckt = None
            elif current_subckt:
                subckt_lines.append(line)
            elif line_lower[0] in self.instance_pattern:
                subckt_calls.append(line)
            else:
                etc_lines.append(line)

        self.subckt_count = len(subckt_definitions.keys())
        print(f"subckt_count: {self.subckt_count}")

        return subckt_definitions, subckt_calls, etc_lines

    def _order_subckts(self, subckt_definitions):
        """ SUBCKT 정의를 의존성에 따라 정렬 """
        dependency_graph = defaultdict(set)

        # 그래프 생성: subckt 간 의존성 정의
        for subckt_name, subckt_lines in subckt_definitions.items():
            for line in subckt_lines:
                if line.lower().startswith("x"):    # instance call
                    called_subckt = [word for word in line.split() if "=" not in word][-1]
                    if called_subckt in subckt_definitions:
                        dependency_graph[subckt_name].add(called_subckt)

        visited = set()
        ordered_subckts = []

        # 의존성 기반 정렬
        def visit(subckt):
            if subckt in visited:
                return
            visited.add(subckt)
            for dependency in dependency_graph[subckt]:
                visit(dependency)
            ordered_subckts.append(subckt)

        for subckt in subckt_definitions:
            if subckt not in visited:
                visit(subckt)

        return ordered_subckts



    def _write_reordered_netlist(self, subckt_definitions, subckt_calls, etc_lines):
        ordered_subckts = self._order_subckts(subckt_definitions)
        self.last_subckt = ordered_subckts[-1] if len(ordered_subckts) > 0 else None
        result_lines = etc_lines
        result_lines.append("")
        # 정렬된 subckt 정의 출력
        for subckt in ordered_subckts:
            result_lines.extend(subckt_definitions[subckt])
            result_lines.append("")    # 서브서킷 간 빈 줄
        # 호출 부분 출력
        result_lines.extend(subckt_calls)
        result_lines.append("")    # 마지막 줄 개행
        return [line + "\n" for line in result_lines]

    def extract_inc_filepath(self, filepath: str) -> list[str]:
        """Extract filepaths only startswith .inc"""
        inc_paths = []
        with open(filepath, "r") as f:
            for l in f:
                if l.strip().lower().startswith(".inc"):
                    match = re.search(r"\.inc\s+['\"]([^'\"]+)['\"]", l)
                    if match:
                        inc_paths.append(match.group(1))
        return inc_paths

    def resolve_path(self, current_file: str, include_path: str) -> str:
        """Convert a relative path to a abs path"""
        if os.path.isabs(include_path):
            return os.path.abspath(include_path)
        else:
            curr_dir = os.path.dirname(current_file)
            return os.path.abspath(os.path.join(curr_dir, include_path))


    def dfs(self, start_file: str, visited_files: None | set = None) -> list[str]:
        if visited_files is None:
            visited = set()

        def dfs_find_all_includes(file_path: str):
            abs_path = os.path.abspath(file_path)

            if abs_path in visited or not os.path.isfile(abs_path):
                if not os.path.isfile(abs_path):
                    print(f"# Warning: File not found: {abs_path}")
                return

            visited.add(abs_path)
            result.append(abs_path)

            include_paths = self.extract_inc_filepath(abs_path)

            for include_path in include_paths:
                resolved_path = self.resolve_path(abs_path, include_path)
                dfs_find_all_includes(resolved_path)

        result = []
        dfs_find_all_includes(start_file)
        return result

    def run(self, input_path, additional_path=None) -> list:
        inc_files = []
        merged_lines = []
        if additional_path is not None:
            inc_files.extend(self.dfs(additional_path))
        inc_files.extend(self.dfs(input_path))
        inc_files.append(input_path)
        print("[inc_files]\n" + "\n".join(inc_files))
        for f in inc_files:
            self._edit_and_merge(f, merged_lines)
        subckt_definitions, subckt_calls, etc_lines = self._parse_netlist(merged_lines)
        reordered_lines = self._write_reordered_netlist(subckt_definitions, subckt_calls, etc_lines)
        return reordered_lines

    def remove_last_subckt(self, out_lst: list) -> list:
        i = len(out_lst) - 1
        comment_pattern = re.compile(r"^\s*([*#]|//)")
        first_valid_line = None
        ends_line_index = None
        subckt_line_index = None

        while i >= 0:
            curr_line = out_lst[i].strip()

            # Skip empty lines or comments
            if not curr_line or comment_pattern.match(curr_line) or curr_line.upper().startswith((".PARAM", ".GLOBAL")):
                i -= 1
                continue

            # Merge with prev line when starting with +
            if curr_line.startswith("+"):
                # Merge continuously
                continuation_lines = []
                while i >= 0 and out_lst[i].strip().startswith("+"):
                    continuation_lines.append(out_lst[i].strip()[1:].strip())
                    i -= 1

                # Not starting with + after starting +
                if i >= 0:
                    base_line = out_lst[i].strip()
                    continuation_lines.reverse()
                    full_line = base_line + " " + " ".join(continuation_lines)
                    curr_line = full_line.strip()
                else:
                    i -= 1
                    continue

            if first_valid_line is None:
                first_valid_line = curr_line.upper()

                if first_valid_line.startswith(".ENDS"):
                    ends_line_index = i
                else:
                    break

            if subckt_line_index is None and curr_line.upper().startswith(".SUBCKT"):
                subckt_line_index = i
                print(f"TOP subckt block found between line {subckt_line_index+1} and {ends_line_index+1} of the output file. The TOP is {curr_line.split()[1]}.")
                break

            i -= 1

        if first_valid_line and first_valid_line.startswith(".ENDS") and ends_line_index is not None and subckt_line_index is not None:

            def is_already_commented(line_text):
                return comment_pattern.match(line_text.strip())

            if not is_already_commented(out_lst[ends_line_index]):
                out_lst[ends_line_index] = "*" + out_lst[ends_line_index]
                print(f"Line {ends_line_index+1} has been commented out.")

            if not is_already_commented(out_lst[subckt_line_index]):
                out_lst[subckt_line_index] = "*" + out_lst[subckt_line_index]
                print(f"Line {subckt_line_index+1} has been commented out.")

            if self.subckt_count > 0:
                self.subckt_count -= 1

        else:
            print("No TOP SUBCKT found.")

        return out_lst

    def make_dummy_subckt(self, out_lst: list) -> list:
        if self.subckt_count == 0:
            dummy_subckt = ["* Dummy subckt for signoff\n", ".subckt dummy\n", ".ends dummy\n", "\n"]
            print("A dummy subckt has been added.")
            return dummy_subckt + out_lst
        else:
            return out_lst


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reorder SPICE netlist by arranging .subckt definitions before instance calls. Convert char into a format readable by SPACE syntax.")
    parser.add_argument("input", help="Path to the original input netlist file path.")
    parser.add_argument("add", nargs="?", help="Path to the additional input netlist file list.")
    parser.add_argument("output", help="Path to the output netlist file.")
    parser.add_argument("-u", "--upper", action="store_true", required=False, help="Make an output in uppercase.")

    args = parser.parse_args()

    # 병합된 파일 생성, 문자열 변환
    obj = NetlistPreprocessing()
    out_lst = obj.run(args.input, args.add)

    # From SOL env_setup.csh
    top_env = os.environ.get("TOP_SUBCKT") if os.environ.get("APP") != "PEC" else os.environ.get("PEC_TOP_SUBCKT")
    if top_env == "" or not top_env:
        out_lst = obj.remove_last_subckt(out_lst)

    # Make dummy subckt if no subckt found
    out_lst = obj.make_dummy_subckt(out_lst)

    with open(args.output, "w") as f:
        if not args.upper:
            f.writelines(f"{line.lower()}" for line in out_lst)
        else:
            f.writelines(f"{line.upper()}" for line in out_lst)
```

--- signoff-dsc-runscript/run.tcl.md ---

run.tcl:

```
set APP $::env(APP)

# Get corner information
set PROCESS $::env(PROCESS)
set VOLTAGE $::env(VOLTAGE)
set TEMPERATURE $::env(TEMPERATURE)

# Get required input files
set NETLIST $::env(NETLIST_FILE)
set EDR $::env(EDR_FILE)
set MP $::env(MP_FILE)
set DISCARD_SUBCKT_FILE $::env(DISCARD_SUBCKT_FILE) ;

# Get simulation parameters
set INPUT_SLOPE $::env(INPUT_SLOPE)
set SIM_TIME $::env(SIMULATION_TIME)
set SIM_TIME_STEP $::env(SIMULATION_TIME_STEP)
set DEFAULT_VOLTAGE $::env(DEFAULT_VOLTAGE)
set HT $::env(HT)
set CT $::env(CT)
set TOP_SUBCKT $::env(TOP_SUBCKT)

# For HBM4
set IS_FINFET $::env(IS_FINFET)
set RAY_MODE $::env(RAY_MODE)


# Optional user defined process corner
if { [info exists ::env(USER_DEFINE_CORNER)] } {
    set USER_CORNER $::env(USER_DEFINE_CORNER)
}

proc get_temperature {} {
    global TEMPERATURE HT CT
    if { $TEMPERATURE eq "HT" } {
        return $HT
    } elseif { $TEMPERATURE eq "CT" } {
        return $CT
    }
}

# Set log file
set_log_file ./LOG/space.log

# Ignore undefined resistance issues
ignore_resistors_having_undefined_resistance
set_default_undefine_resistance 1.0
set_default_undefine_vdd_value $DEFAULT_VOLTAGE


# Set hierarchy separator
set_hierarchy_separator "."

# Read technology files
source ./SETUP/set_power.tcl
add_passive_resistor_subckt [file_to_list "passive_resistor_subckt_list.tcl"]

if { $EDR ne "" } {
    if { [string equal -nocase $IS_FINFET "false"] } {
        read_tech_file ./SETUP/tech_file
    } else {
        read_mp_model "$MP"
        set_mp_file -mp_file "$MP" -corner $PROCESS
        set_edr_file "empty.edr"
    }
}

if { $DISCARD_SUBCKT_FILE ne "" } {
    add_discard_subckt [file_to_list $DISCARD_SUBCKT_FILE]
}


# Read netlist and build design
read_spice_netlist $NETLIST

if {$TOP_SUBCKT ne ""} {
    build_design $TOP_SUBCKT
} else {
    build_design ""
}

# Prepare common arguments for driver_size_check
set common_args "-slope $INPUT_SLOPE -time $SIM_TIME -step $SIM_TIME_STEP -temperature \[get_temperature\] -thread"

if { [string equal -nocase $IS_FINFET "True"] } {
    append common_args " -scale 1"
}

# Add -no_simulation flag conditionally
if { [string equal -nocase $RAY_MODE "True"] } {
    append common_args " -no_simulation"
}

# Run Driver Size Check
eval "driver_size_check $common_args -o ./RESULT/result"


exit
```

--- signoff-dsc-runscript/run.sh.md ---

run.sh:
```
#!/bin/csh -f

# Setup environment
/user/signoff.dsa/launcher/utils/set_input_env.py
source env_setup.csh
setenv OUTPUT_FILENAME "result"

# Configuration
set additional_netlist_list = "SETUP/additional_netlist"
set output_netlist = "SETUP/merged_netlist"
set NET_PRE_PATH = /appl/LINUX/Signoff/scripts


# Initialize
$UPDATE_CONFIG --start --msg "Initializing"

# Check if netlist is compressed
if ("`echo $NETLIST_FILE | tr '[A-Z]' '[a-z]'`" =~ "*.gz") then
    echo "Error: $NETLIST_FILE is compressed. Please decompress it first."
    echo "Use: gunzip $NETLIST_FILE"
    exit 1
endif


# Edit netlist for FinFET
if ("`echo $IS_FINFET | tr '[a-z]' '[A-Z]'`" == "TRUE" && "`echo $NETLIST_FILE | tr '[A-Z]' '[a-z]'`" !~ "*.cvt") then
    $UPDATE_CONFIG --msg "Editing netlist for FinFET"

    # No additional netlist (ex. rmres_2t.inc lvsres.inc ...)
    if ($ADDITIONAL_NETLIST_INPUT == "") then
        $NET_PRE_PATH/netlist_preprocessing.py "$NETLIST_FILE" "$output_netlist"

    # Additional netlist
    else
        cat $ADDITIONAL_NETLIST_INPUT > $additional_netlist_list
        $NET_PRE_PATH/netlist_preprocessing.py "$NETLIST_FILE" "$additional_netlist_list" "$output_netlist"
    endif

    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Editing netlist failed"
        exit 1
    endif

    unsetenv NETLIST_FILE
    setenv NETLIST_FILE "$output_netlist"
endif

# Preprocessing
$UPDATE_CONFIG --msg "Preprocessing"
python pre_setting.py
if ($status != 0) then
    $UPDATE_CONFIG  --fail --msg "Preprocessing failed"
    exit 1
endif

# Main simulation
$UPDATE_CONFIG --msg "Running simulation"
# Ray mode specific processing
if ( $RAY_MODE == True ) then
    space_sub -Is -cpu 16 -mem 300000 -scv run.tcl
    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Simulation failed"
        exit 1
    endif

    $UPDATE_CONFIG --msg "Deck Simulation with ray"
    cp /user/signoff.dsa/ray/ray_dsc_pipeline.py ./
    ray_space_sub -Is -deck-dir .deck -output-dir ./ray_out -simulator primesim
    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Simulation(Ray) failed"
        exit 1
    endif
else
    #python /user/signoff.dev/bin/lsf_job_lose_ctrl.py . &   
    python /user/signoff.dev/bin/lsf_job_lose_ctrl.py . $$ &
    space_sub -Is -cpu 8 -mem 300000 -scv run.tcl
    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Simulation failed"
        exit 1
    endif

    # Postprocessing
    $UPDATE_CONFIG --msg "Postprocessing"
    python make_csv.py
    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Postprocessing failed"
        exit 1
    endif
endif

# Job completed successfully
$UPDATE_CONFIG --done --msg "DSC executed successfully"

exit
```

--- signoff-dsc-runscript/pre_setting.py.md ---

pre_setting.py:

```
import os

def write_tech(mp_file, edr_file, process_corner, rpass_file=""):
  tech_file = open("./SETUP/tech_file", "w")

  # EDR/MP/SPC file include
  tech_file.write(".inc\t" + f"'{edr_file}'" + "\n")
  tech_file.write(".lib\t" + f"'{mp_file}'" + "\t" + process_corner.lower() + "\n")
  # tech_file.write('.inc\t' + f"'{spc_file}'" + '\n')

  # RPASS file이 있는 경우
  if rpass_file:
    tech_file.write(".lib\t" + f"'{rpass_file}'" + "\t")
    if process_corner[0].upper() == "S":
      tech_file.write("s\n")
    elif process_corner[0].upper() == "F":
      tech_file.write("f\n")
    else:
      tech_file.write("t\n")

  tech_file.close()


def write_power(voltage_corner):
  """Power/Ground list 파일 생성
  Args:
    voltage_corner: Voltage corner (HV/LV)
  """
  power_tcl = open("./SETUP/set_power.tcl", "w")

  if voltage_corner == "LV":
    vdd_list_file = os.environ["LV_VDD_LIST_FILE"]
    gnd_list_file = os.environ["LV_GND_LIST_FILE"]
  elif voltage_corner == "HV":
    vdd_list_file = os.environ["HV_VDD_LIST_FILE"]
    gnd_list_file = os.environ["HV_GND_LIST_FILE"]
  else:
    return

  # VDD list
  power_tcl.write("# VDD POWER Setting\n")
  with open(vdd_list_file) as f:
    for line in f.readlines():
      line = line.strip()
      if line and "=" in line:
        node, voltage = line.split("=")
        if "/" in node:
          power_tcl.write(f"set_vdd {node} -voltage {voltage} -local\n")
        else:
          power_tcl.write(f"set_vdd {node} -voltage {voltage}\n")
  power_tcl.write("\n")

  # GND list
  power_tcl.write("# GND POWER Setting\n")
  with open(gnd_list_file) as f:
    for line in f.readlines():
      line = line.strip()
      if line and "=" in line:
        node, voltage = line.split("=")
        if "/" in node:
          power_tcl.write(f"set_gnd {node} -voltage {voltage} -local\n")
        else:
          power_tcl.write(f"set_gnd {node} -voltage {voltage}\n")

  power_tcl.close()


# Get application name and corner info from environment
app_name = os.environ["APP"]

# Get input file paths
mp_file = os.environ["MP_FILE"]
edr_file = os.environ["EDR_FILE"]
spc_file = os.environ["NETLIST_FILE"]
rpass_file = os.environ.get("RPASS_FILE", "")  # Optional

# Get corner setup if exists
process_corner = os.environ.get(f"PROCESS", "TT")  # Default TT
voltage_corner = os.environ.get(f"VOLTAGE", "")
temp_corner = os.environ.get(f"TEMPERATURE", "")

# Handle user defined corner
if process_corner == "UD":
  process_corner = os.environ.get("USER_DEFINE_SIM_CORNER_PROCESS", "TT")

# Create SETUP directory
os.makedirs("./SETUP", exist_ok=True)
# Create RESULT directory
os.makedirs("./RESULT", exist_ok=True)


# Write technology setup file
write_tech(mp_file=mp_file, edr_file=edr_file, process_corner=process_corner, rpass_file=rpass_file)

# Write power setup file if voltage corner exists
if voltage_corner:
  write_power(voltage_corner)


```

--- signoff-dsc-runscript/input_config.yaml.md ---

input_config.yaml:
```
DSC:
 color: "#4263eb" # Blue
 label: "Driver Size Check (DSC)"
 manual_link: "https://dsplm.sec.samsung.net/mem/dsc"
 mlm_link: "https://mlm.jira.samsungds.net/projects/SPACE/issues/"
 developer: ['deepwonwoo']
 inputs:
  - name: NETLIST_FILE
   type: file_input
   required: true 
   default: "xr_pad_231128.star"
   description: "Circuit netlist file in SPICE format"

  - name: EDR_FILE 
   type: file_input
   required: true
   default: "Zenith_XR_EDR"
   description: "EDR file for defining extra device rules"

  - name: MP_FILE
   type: file_input 
   required: true
   default: "Zenith_XR_MP"
   description: "Model parameter file defining simulation models"

  - name: TOP_SUBCKT 
   type: text_input
   required: false
   description: "Top-level subcircuit name"

  - name: DISCARD_SUBCKT_FILE
   type: file_input
   required: false
   default: ""
   description: "Discard subckt file path"

  - name: DEFAULT_VOLTAGE
   type: number_input
   required: true 
   default: 0.96
   unit: "V"
   description: "Default voltage value for undefined nodes"

  - name: INPUT_SLOPE
   type: number_input
   required: true
   default: 0.4
   unit: "ns"
   description: "Input signal transition time"
   
  - name: SIMULATION_TIME
   type: number_input
   required: true
   default: 10
   unit: "ns"
   description: "Total simulation time period"
   
  - name: SIMULATION_TIME_STEP
   type: number_input
   required: true
   default: 0.01
   unit: "ns"
   description: "Time step for simulation (ns)"

  - name: USERDEFINE_CORNER
   type: text_input
   required: false 
   default: ""
   description: "Custom simulation corner specification (optional)"

  - name: RPASS_FILE
   type: file_input
   required: false
   default: ""
   description: "Pass transistor model file (optional)"

  - name: IS_FINFET
   type: select_input
   required: true
   datas: ['FALSE', 'TRUE']
   default: 'FALSE'
   description: "Select TRUE if the product is using FinFET"

  - name: ADDITIONAL_NETLIST_INPUT
   type: file_input
   required: false
   default: ""
   description: "Additional netlist file list(with .inc)"

  - name: RAY_MODE
   type: checkbox_input
   required: false
   description: "Run Simulations in Ray Cluster"

 pvt_inputs:
  - name: PROCESS
   default: SS
   type: text_input
   
  - name: VOLTAGE
   default: HV
   type: text_input

  - name: TEMPERATURE
   default: HT
   type: text_input

  - name: HT
   type: number_input 
   required: true
   default: 100
   description: "High temperature value for simulation"
   unit: "°C"
   depends_on:
    TEMPERATURE: "HT"
   
  - name: CT
   type: number_input
   required: true 
   default: -10
   description: "Cold temperature value for simulation"
   unit: "°C"
   depends_on:
    TEMPERATURE: "CT"

  - name: LV_VDD_LIST_FILE
   type: file_input
   required: true
   default: "vdd_list"
   description: "File containing low voltage VDD node list"
   depends_on:
    VOLTAGE: "LV"
    
  - name: LV_GND_LIST_FILE 
   type: file_input
   required: true
   default: "gnd_list"
   description: "File containing low voltage GND node list" 
   depends_on:
    VOLTAGE: "LV"
    
  - name: HV_VDD_LIST_FILE
   type: file_input
   required: true
   default: "vdd_list"
   description: "File containing high voltage VDD node list"
   depends_on:
    VOLTAGE: "HV"
   
  - name: HV_GND_LIST_FILE
   type: file_input
   required: true
   default: "gnd_list"
   description: "File containing high voltage GND node list"
   depends_on:
    VOLTAGE: "HV"
```

--- signoff-dsc-runscript/signoff-dsc-runscript.md ---


run.sh:
```
#!/bin/csh -f

# Setup environment
/user/signoff.dsa/launcher/utils/set_input_env.py
source env_setup.csh
setenv OUTPUT_FILENAME "result"

# Configuration
set additional_netlist_list = "SETUP/additional_netlist"
set output_netlist = "SETUP/merged_netlist"
set NET_PRE_PATH = /appl/LINUX/Signoff/scripts


# Initialize
$UPDATE_CONFIG --start --msg "Initializing"

# Check if netlist is compressed
if ("`echo $NETLIST_FILE | tr '[A-Z]' '[a-z]'`" =~ "*.gz") then
    echo "Error: $NETLIST_FILE is compressed. Please decompress it first."
    echo "Use: gunzip $NETLIST_FILE"
    exit 1
endif


# Edit netlist for FinFET
if ("`echo $IS_FINFET | tr '[a-z]' '[A-Z]'`" == "TRUE" && "`echo $NETLIST_FILE | tr '[A-Z]' '[a-z]'`" !~ "*.cvt") then
    $UPDATE_CONFIG --msg "Editing netlist for FinFET"

    # No additional netlist (ex. rmres_2t.inc lvsres.inc ...)
    if ($ADDITIONAL_NETLIST_INPUT == "") then
        $NET_PRE_PATH/netlist_preprocessing.py "$NETLIST_FILE" "$output_netlist"

    # Additional netlist
    else
        cat $ADDITIONAL_NETLIST_INPUT > $additional_netlist_list
        $NET_PRE_PATH/netlist_preprocessing.py "$NETLIST_FILE" "$additional_netlist_list" "$output_netlist"
    endif

    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Editing netlist failed"
        exit 1
    endif

    unsetenv NETLIST_FILE
    setenv NETLIST_FILE "$output_netlist"
endif

# Preprocessing
$UPDATE_CONFIG --msg "Preprocessing"
python pre_setting.py
if ($status != 0) then
    $UPDATE_CONFIG  --fail --msg "Preprocessing failed"
    exit 1
endif

# Main simulation
$UPDATE_CONFIG --msg "Running simulation"
# Ray mode specific processing
if ( $RAY_MODE == True ) then
    space_sub -Is -cpu 16 -mem 300000 -scv run.tcl
    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Simulation failed"
        exit 1
    endif

    $UPDATE_CONFIG --msg "Deck Simulation with ray"
    cp /user/signoff.dsa/ray/ray_dsc_pipeline.py ./
    ray_space_sub -Is -deck-dir .deck -output-dir ./ray_out -simulator primesim
    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Simulation(Ray) failed"
        exit 1
    endif
else
    #python /user/signoff.dev/bin/lsf_job_lose_ctrl.py . &   
    python /user/signoff.dev/bin/lsf_job_lose_ctrl.py . $$ &
    space_sub -Is -cpu 8 -mem 300000 -scv run.tcl
    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Simulation failed"
        exit 1
    endif

    # Postprocessing
    $UPDATE_CONFIG --msg "Postprocessing"
    python make_csv.py
    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Postprocessing failed"
        exit 1
    endif
endif

# Job completed successfully
$UPDATE_CONFIG --done --msg "DSC executed successfully"

exit
```

run.tcl:

```
set APP $::env(APP)

# Get corner information
set PROCESS $::env(PROCESS)
set VOLTAGE $::env(VOLTAGE)
set TEMPERATURE $::env(TEMPERATURE)

# Get required input files
set NETLIST $::env(NETLIST_FILE)
set EDR $::env(EDR_FILE)
set MP $::env(MP_FILE)
set DISCARD_SUBCKT_FILE $::env(DISCARD_SUBCKT_FILE) ;

# Get simulation parameters
set INPUT_SLOPE $::env(INPUT_SLOPE)
set SIM_TIME $::env(SIMULATION_TIME)
set SIM_TIME_STEP $::env(SIMULATION_TIME_STEP)
set DEFAULT_VOLTAGE $::env(DEFAULT_VOLTAGE)
set HT $::env(HT)
set CT $::env(CT)
set TOP_SUBCKT $::env(TOP_SUBCKT)

# For HBM4
set IS_FINFET $::env(IS_FINFET)
set RAY_MODE $::env(RAY_MODE)


# Optional user defined process corner
if { [info exists ::env(USER_DEFINE_CORNER)] } {
    set USER_CORNER $::env(USER_DEFINE_CORNER)
}

proc get_temperature {} {
    global TEMPERATURE HT CT
    if { $TEMPERATURE eq "HT" } {
        return $HT
    } elseif { $TEMPERATURE eq "CT" } {
        return $CT
    }
}

# Set log file
set_log_file ./LOG/space.log

# Ignore undefined resistance issues
ignore_resistors_having_undefined_resistance
set_default_undefine_resistance 1.0
set_default_undefine_vdd_value $DEFAULT_VOLTAGE


# Set hierarchy separator
set_hierarchy_separator "."

# Read technology files
source ./SETUP/set_power.tcl
add_passive_resistor_subckt [file_to_list "passive_resistor_subckt_list.tcl"]

if { $EDR ne "" } {
    if { [string equal -nocase $IS_FINFET "false"] } {
        read_tech_file ./SETUP/tech_file
    } else {
        read_mp_model "$MP"
        set_mp_file -mp_file "$MP" -corner $PROCESS
        set_edr_file "empty.edr"
    }
}

if { $DISCARD_SUBCKT_FILE ne "" } {
    add_discard_subckt [file_to_list $DISCARD_SUBCKT_FILE]
}


# Read netlist and build design
read_spice_netlist $NETLIST

if {$TOP_SUBCKT ne ""} {
    build_design $TOP_SUBCKT
} else {
    build_design ""
}

# Prepare common arguments for driver_size_check
set common_args "-slope $INPUT_SLOPE -time $SIM_TIME -step $SIM_TIME_STEP -temperature \[get_temperature\] -thread"

if { [string equal -nocase $IS_FINFET "True"] } {
    append common_args " -scale 1"
}

# Add -no_simulation flag conditionally
if { [string equal -nocase $RAY_MODE "True"] } {
    append common_args " -no_simulation"
}

# Run Driver Size Check
eval "driver_size_check $common_args -o ./RESULT/result"


exit
```


* input_config.yaml:
```
DSC:
 color: "#4263eb" # Blue
 label: "Driver Size Check (DSC)"
 manual_link: "https://dsplm.sec.samsung.net/mem/dsc"
 mlm_link: "https://mlm.jira.samsungds.net/projects/SPACE/issues/"
 developer: ['deepwonwoo']
 inputs:
  - name: NETLIST_FILE
   type: file_input
   required: true 
   default: "xr_pad_231128.star"
   description: "Circuit netlist file in SPICE format"

  - name: EDR_FILE 
   type: file_input
   required: true
   default: "Zenith_XR_EDR"
   description: "EDR file for defining extra device rules"

  - name: MP_FILE
   type: file_input 
   required: true
   default: "Zenith_XR_MP"
   description: "Model parameter file defining simulation models"

  - name: TOP_SUBCKT 
   type: text_input
   required: false
   description: "Top-level subcircuit name"

  - name: DISCARD_SUBCKT_FILE
   type: file_input
   required: false
   default: ""
   description: "Discard subckt file path"

  - name: DEFAULT_VOLTAGE
   type: number_input
   required: true 
   default: 0.96
   unit: "V"
   description: "Default voltage value for undefined nodes"

  - name: INPUT_SLOPE
   type: number_input
   required: true
   default: 0.4
   unit: "ns"
   description: "Input signal transition time"
   
  - name: SIMULATION_TIME
   type: number_input
   required: true
   default: 10
   unit: "ns"
   description: "Total simulation time period"
   
  - name: SIMULATION_TIME_STEP
   type: number_input
   required: true
   default: 0.01
   unit: "ns"
   description: "Time step for simulation (ns)"

  - name: USERDEFINE_CORNER
   type: text_input
   required: false 
   default: ""
   description: "Custom simulation corner specification (optional)"

  - name: RPASS_FILE
   type: file_input
   required: false
   default: ""
   description: "Pass transistor model file (optional)"

  - name: IS_FINFET
   type: select_input
   required: true
   datas: ['FALSE', 'TRUE']
   default: 'FALSE'
   description: "Select TRUE if the product is using FinFET"

  - name: ADDITIONAL_NETLIST_INPUT
   type: file_input
   required: false
   default: ""
   description: "Additional netlist file list(with .inc)"

  - name: RAY_MODE
   type: checkbox_input
   required: false
   description: "Run Simulations in Ray Cluster"

 pvt_inputs:
  - name: PROCESS
   default: SS
   type: text_input
   
  - name: VOLTAGE
   default: HV
   type: text_input

  - name: TEMPERATURE
   default: HT
   type: text_input

  - name: HT
   type: number_input 
   required: true
   default: 100
   description: "High temperature value for simulation"
   unit: "°C"
   depends_on:
    TEMPERATURE: "HT"
   
  - name: CT
   type: number_input
   required: true 
   default: -10
   description: "Cold temperature value for simulation"
   unit: "°C"
   depends_on:
    TEMPERATURE: "CT"

  - name: LV_VDD_LIST_FILE
   type: file_input
   required: true
   default: "vdd_list"
   description: "File containing low voltage VDD node list"
   depends_on:
    VOLTAGE: "LV"
    
  - name: LV_GND_LIST_FILE 
   type: file_input
   required: true
   default: "gnd_list"
   description: "File containing low voltage GND node list" 
   depends_on:
    VOLTAGE: "LV"
    
  - name: HV_VDD_LIST_FILE
   type: file_input
   required: true
   default: "vdd_list"
   description: "File containing high voltage VDD node list"
   depends_on:
    VOLTAGE: "HV"
   
  - name: HV_GND_LIST_FILE
   type: file_input
   required: true
   default: "gnd_list"
   description: "File containing high voltage GND node list"
   depends_on:
    VOLTAGE: "HV"
```


pre_setting.py:

```
import os

def write_tech(mp_file, edr_file, process_corner, rpass_file=""):
  tech_file = open("./SETUP/tech_file", "w")

  # EDR/MP/SPC file include
  tech_file.write(".inc\t" + f"'{edr_file}'" + "\n")
  tech_file.write(".lib\t" + f"'{mp_file}'" + "\t" + process_corner.lower() + "\n")
  # tech_file.write('.inc\t' + f"'{spc_file}'" + '\n')

  # RPASS file이 있는 경우
  if rpass_file:
    tech_file.write(".lib\t" + f"'{rpass_file}'" + "\t")
    if process_corner[0].upper() == "S":
      tech_file.write("s\n")
    elif process_corner[0].upper() == "F":
      tech_file.write("f\n")
    else:
      tech_file.write("t\n")

  tech_file.close()


def write_power(voltage_corner):
  """Power/Ground list 파일 생성
  Args:
    voltage_corner: Voltage corner (HV/LV)
  """
  power_tcl = open("./SETUP/set_power.tcl", "w")

  if voltage_corner == "LV":
    vdd_list_file = os.environ["LV_VDD_LIST_FILE"]
    gnd_list_file = os.environ["LV_GND_LIST_FILE"]
  elif voltage_corner == "HV":
    vdd_list_file = os.environ["HV_VDD_LIST_FILE"]
    gnd_list_file = os.environ["HV_GND_LIST_FILE"]
  else:
    return

  # VDD list
  power_tcl.write("# VDD POWER Setting\n")
  with open(vdd_list_file) as f:
    for line in f.readlines():
      line = line.strip()
      if line and "=" in line:
        node, voltage = line.split("=")
        if "/" in node:
          power_tcl.write(f"set_vdd {node} -voltage {voltage} -local\n")
        else:
          power_tcl.write(f"set_vdd {node} -voltage {voltage}\n")
  power_tcl.write("\n")

  # GND list
  power_tcl.write("# GND POWER Setting\n")
  with open(gnd_list_file) as f:
    for line in f.readlines():
      line = line.strip()
      if line and "=" in line:
        node, voltage = line.split("=")
        if "/" in node:
          power_tcl.write(f"set_gnd {node} -voltage {voltage} -local\n")
        else:
          power_tcl.write(f"set_gnd {node} -voltage {voltage}\n")

  power_tcl.close()


# Get application name and corner info from environment
app_name = os.environ["APP"]

# Get input file paths
mp_file = os.environ["MP_FILE"]
edr_file = os.environ["EDR_FILE"]
spc_file = os.environ["NETLIST_FILE"]
rpass_file = os.environ.get("RPASS_FILE", "")  # Optional

# Get corner setup if exists
process_corner = os.environ.get(f"PROCESS", "TT")  # Default TT
voltage_corner = os.environ.get(f"VOLTAGE", "")
temp_corner = os.environ.get(f"TEMPERATURE", "")

# Handle user defined corner
if process_corner == "UD":
  process_corner = os.environ.get("USER_DEFINE_SIM_CORNER_PROCESS", "TT")

# Create SETUP directory
os.makedirs("./SETUP", exist_ok=True)
# Create RESULT directory
os.makedirs("./RESULT", exist_ok=True)


# Write technology setup file
write_tech(mp_file=mp_file, edr_file=edr_file, process_corner=process_corner, rpass_file=rpass_file)

# Write power setup file if voltage corner exists
if voltage_corner:
  write_power(voltage_corner)


```