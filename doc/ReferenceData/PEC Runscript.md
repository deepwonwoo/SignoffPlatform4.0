signoff-pt-signoff

run.sh:
```
#!/bin/csh

/user/signoff.dsa/launcher/utils/set_input_env.py
source env_setup.csh

setenv NETLIST_FILE $PEC_NETLIST_FILE
setenv DISCARD_SUBCKT_FILE $PEC_DISCARD_SUBCKTS
set additional_netlist_list = "SETUP/additional_netlist" # For FinFET
set output_netlist = "SETUP/merged_netlist" # For FinFET
set NET_PRE_PATH = /user/signoff.dev/lsj/DEV/netlist_preprocessing # For FinFET
set QUERY_PATH = /user/memorypjt/APPS/pec_signoff
set finfet = 0

$UPDATE_CONFIG --start --msg "Preprocessing"

# Edit netlist for FinFET
if ("`echo $IS_FINFET | tr '[a-z]' '[A-Z]'`" == "TRUE") then
    set finfet = 1
    $UPDATE_CONFIG --msg "Editing netlist for FinFET"
    echo "Editing netlist for FinFET"

    # No additional netlist (ex. rmres_2t.inc lvsres.inc ...)
    if ($ADDITIONAL_NETLIST_INPUT == "") then
        $NET_PRE_PATH/netlist_preprocessing.py "$NETLIST_FILE" "$output_netlist"

    # Additional netlist
    else
        cat $ADDITIONAL_NETLIST_INPUT > $additional_netlist_list
        $NET_PRE_PATH/netlist_preprocessing.py "$NETLIST_FILE" "$additional_netlist_list" "$output_netlist"
    endif

    unsetenv NETLIST_FILE
    setenv NETLIST_FILE "$output_netlist"
endif
if ($status != 0) then
    $UPDATE_CONFIG --fail --msg "Editing netlist failed"
    echo "Editing netlist failed"
    exit 1
endif

# MBV Process
if ($MBV_PRODUCT != "" && $MBV_PRODUCT != "NONE") then
    $UPDATE_CONFIG --msg "Querying MBV table"
    echo "Querying MBV table"
    $QUERY_PATH/pec_bv -d $MBV_PRODUCT

    set mbv_csv = "${MBV_PRODUCT}_BV.csv"
    if (! -e $mbv_csv) then
        if (-e "LOCAL_MBV_TABLE/${mbv_csv}") then
            set mbv_csv = "LOCAL_MBV_TABLE/${mbv_csv}"
            echo "Using Local MBV table: ${mbv_csv}"
        else
            $UPDATE_CONFIG --fail --msg "Error Querying MBV table"
            echo "Error Querying MBV table"
            exit 1
        endif
    endif
endif

if ($?mbv_csv) then
    python SCRIPTS/modify_bv_file.py $mbv_csv $VDD_FILE $GND_FILE
    if ($status != 0) then
        $UPDATE_CONFIG --fail --msg "Error converting MBV table"
        echo "Error converting MBV table"
        exit 1
    endif
endif

# Vth Process
if (($USER_VTH == "" || $VTH_PRODUCT != "") && $VTH_PRODUCT != "NONE") then
    $UPDATE_CONFIG --msg "Processing VTH table"
    set vth_csv = `python SCRIPTS/vth_wrapper.py`
endif
if ($status != 0) then
    $UPDATE_CONFIG --fail --msg "Error preprocessing VTH"
    echo "Error preprcessing VTH"
endif
echo "Using VTH table: ${vth_csv}"

# Running SPACE
if ($finfet != 1) then
    $UPDATE_CONFIG --msg "Running SPACE"
    echo "Running SPACE"
    printf "exit\n" | space_sub -Is -scv pec.tcl
else
    $UPDATE_CONFIG --msg "Running SPACE in FinFET mode"
    echo "Running SPACE in FinFET mode"
    source "/user/space.dev/lsj/SPACE_DEV_cwyoo/space_hbm/env"
    bsub -Is -env "all" -app space -q unite -n 8 -R "type == LINUX64 span[hosts=1] rusage[mem=250000]" < SCRIPTS/finfet_wrapper.csh
endif
if ($status != 0) then
    $UPDATE_CONFIG --fail --msg "Error running SPACE"
    echo "Error running SPACE"
    exit 1
endif

# Postproces
$UPDATE_CONFIG --msg "Postprocessing"
echo "Postprocessing"
python SCRIPTS/create_result.py LOG/space.log RESULT/
if ($status != 0) then
    $UPDATE_CONFIG --fail --msg "Error creating result.csv"
    echo "Error creating result.csv"
    exit 1
endif

# @251104: fet_info.out converting script added
$UPDATE_CONFIG --msg "Making fet_info.csv"
echo "Making fet_info.csv"
python SCRIPTS/convert_fet_info.py fet_info.out -o fet_info.csv
if ($status != 0) then
    $UPDATE_CONFIG --fail --msg "Error converting fet_info.out to csv file"
    echo "Error converting fet_info.out to csv file"
    exit 1
endif

$UPDATE_CONFIG --done --msg "PEC executed successfully"
echo "PEC executed successfully"

```

input_config.yaml:

```
PEC:
  color: '#757575'
  label: Power Error Check (PEC)
  manual_link: "https://dsplm.sec.samsung.net/mem"
  mlm_link: "https://mlm.jira.samsungds.net/"
  developer: ['sj90.lee']
  conditional_input_flow:
    - flows: ["Normal", "Test", "Test2"]
    - flow_names: ["Normal", "Test", "Test2"]
      description: Top VDD list file
      name: VDD_FILE
      type: file_input
      required: true
      default: /PEC/DB/normal_vdd_V20
      placeholder: Enter all positive powers and feedbacks(ex_ vpp_feedback=3.0) on TOP. Hierarchical powers can be declared(ex_ x_pad.vref=0.6)
    - flow_names: ["Normal", "Test", "Test2"]
      description: Top GND list file
      name: GND_FILE
      type: file_input
      required: true
      default: /PEC/DB/normal_gnd_V10
      placeholder: Enter all gnds, negative powers and feedbacks(ex_ vbb2_feedback=-0.1) on TOP. Hierarchical powers can be declared(ex_ x_pad.vbne_pad=-0.9)
      
    - flow_names: ["Normal", "Test", "Test2"]
      description: (optional) Top pin list file path to block voltage propagation
      name: PIN_FILE
      type: file_input
      required: false
      default: /PEC/PIN/INPUT/pin_list
      placeholder: (optional) Top pin list to block voltage propagation
    - flow_names: ["Normal", "Test", "Test2"]
      description: (optional) Top pin list to compare between Bdie and Cdie. Both [PIN File] and [PIN To Compare] are needed.
      name: PIN_TO_COMPARE
      type: file_input
      required: false
      placeholder: (optional) Top pin list to compare between Bdie and Cdie. Both [Pin File] and [Pin To Compare] are needed.

  inputs:
    - default: /CKT/XR_FULLCHIP.ckt
      description: CKT netlist file path
      name: PEC_NETLIST_FILE
      required: true
      type: file_input
      placeholder: ex) /PEC/DB/VM_FULLCHIP_NOCORE.ckt
    - default: /user/l432gxr00/PARAM/LINK/Zenith_XR_MP
      description: Model parameter file defining simulation models
      name: MP_FILE
      required: true
      type: file_input
      placeholder: ex) /PARAM/ABS_VH_MP
    - default: /user/l432gxr00/PARAM/LINK/Zenith_XR_EDR
      description: EDR file for defining extra device rules
      name: EDR_FILE
      required: true
      type: file_input
      placeholder: ex) /PARAM/ABS_VM_EDR
    - datas: [UA, VC, SK, SD, UD, NONE]
      default: XR
      description: Product name to check MBV rule
      name: MBV_PRODUCT
      required: true
      type: select_input
    - datas: [UA, VC, SK, SD, UD, CUSTOM, NONE]
      default: XR
      description: Product name to check VTH rule
      name: VTH_PRODUCT
      required: true
      type: select_input
    - datas: ['-25', '85', '-40']
      default: '-25'
      description: Temperature corner to check VTH rule
      name: VTH_TEMPERATURE
      required: true
      type: select_input
    - default: ''
      description: User VTH table (optional)
      name: USER_VTH
      required: false
      type: file_input
      placeholder: (optional) ex) User vth table. Works when Vth Product is CUSTOM.
    - datas: [SS, TT, NONE]
      default: SS
      description: Process corner to check VTH rule
      name: VTH_CORNER
      required: true
      type: select_input
    - description: Top-level subcircuit name (optional, if not specified uses the netlist top subcircuit)
      name: PEC_TOP_SUBCKT
      required: true
      type: text_input
      placeholder: ex) VM_FULLCHIP
    - default: ''
      description: Pass transistor model file (optional)
      name: RPASS_FILE
      required: false
      type: file_input
      placeholder: (optional)
    - default: ''
      description: Set Virtual power and ground as power family
      name: POWER_FAMILY_LIST_FILE
      required: false
      type: file_input
      placeholder: (optional)
    - default: ''
      description: Source-controlled level shifter list NOT to check Multiple Power rule
      name: LEVEL_SHIFTER_MASTER_LIST_FILE
      required: false
      type: file_input
      placeholder: (optional)
    - default: ''
      description: Constraint file to check Wrong Power to FET rule
      name: MODEL_VDD_CONSTRAINT_FILE
      required: false
      type: file_input
      placeholder: (optional)
    - datas: ['LATEST', '2099.99.99']
      default: 'LATEST'
      description: PEC Version
      name: PEC_VERSION
      required: false
      type: select_input
    - datas: ['False', 'True']
      default: 'False'
      description: Enable Hierarchical PEC
      name: HPEC
      required: false
      type: select_input
    - default: ''
      description: Antenna diode models to check Wrong Antenna Diode Direction rule
      name: ANTENNA_DIODE_MASTER
      required: false
      type: text_input
      placeholder: (optional) ex) ant_np ant_pn
    - description: Subckts to discard (optional)
      name: PEC_DISCARD_SUBCKTS
      required: false
      type: text_input
      placeholder: (optional) ex) F_ARRAY_1WL
    - name: IS_FINFET
      type: select_input
      required: true
      datas: ['False', 'True']
      default: 'False'
      description: "Select TRUE if the product is using FinFET"
    - name: ADDITIONAL_NETLIST_INPUT
      type: file_input
      required: false
      default: finfet_additional_netlist.inc
      description: "Additional netlist file list(with .inc)"
      placeholder: (optional)
```
