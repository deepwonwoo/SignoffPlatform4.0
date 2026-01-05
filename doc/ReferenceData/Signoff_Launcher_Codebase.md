# Directory Structure
```
assets/
  dashAgGridComponentFunctions.js
job_run/
  actions/
    log.py
    remove.py
    rerun.py
    result.py
    stop.py
    terminal.py
  job_info.py
  jobFiltering.py
  jobMonitoring.py
  jobTable.py
  page.py
job_set/
  jobCards.py
  jobInputs.py
  jobManager.py
  jobQueue.py
  page.py
RUNSCRIPTS/
  DSC/
    input_config.yaml
    make_csv.py
    netlist_preprocessing.py
    pre_setting.py
    run.sh
    run.tcl
  LS/
    input_config.yaml
    run.sh
utils/
  config_loader.py
  devworks_api.py
  logger.py
  lsf.py
  manual_link.py
  set_input_env.py
  settings.py
  sol_constants.py
  update_config.py
  workspace.py
workspace/
  LS_SSPHVCT_20250318_01/
    job_config.yaml
app.py
signoff_applications.yaml
```

# Files

## File: assets/dashAgGridComponentFunctions.js
```javascript
var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};


// Status 표시를 위한 컴포넌트
dagcomponentfuncs.StatusIndicator = function(props) {
    const status = props.value || 'None';
    const colors = {
        'pending': '#FFA500',
        'running': '#4CAF50',
        'done': '#2196F3',
        'failed': '#F44336',
        'None': '#9E9E9E'
    };
    
    return React.createElement('div', {
        style: {
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
        }
    }, [
        React.createElement('span', {
            style: {
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: colors[status.toLowerCase()],
                display: 'inline-block'
            }
        }),
        React.createElement('span', {}, status)
    ]);
};

// Action 버튼들을 위한 컴포넌트
dagcomponentfuncs.ActionButtons = function (props) {
    
    // props 및 data가 존재하는지 확인
    if (!props || !props.data) {
        return React.createElement('div', {style: {display: 'flex', gap: '8px'}}, []);
    }

    const {setData, data} = props;

    // 상태별 버튼 활성화 여부 확인
    const status = (data.status || '').toLowerCase();
    const isRunning = status === 'running';
    const isPending = status === 'pending';
    const isDone = status === 'done';

    const isDeletable = !isRunning;
    const isStoppable = isRunning || isPending;
    const canRerun = ['done', 'failed'].includes(status);


    function handleAction(action) {
        if (setData) {
          setData(action);
        }
      }
    
    function getRemoveButtonTitle(status) {
        if (isRunning) return 'Cannot remove running job';
        if (isPending) return 'Cannot remove pending job';
        return 'Remove this job';
    }
    
    
    return React.createElement('div', {
        style: {
            display: 'flex',
            gap: '8px'
        }
    }, [
        // Play button
        React.createElement(window.dash_blueprint_components.Button, {
            icon: 'reset',
            minimal: true,
            small: true,
            intent: 'success',
            disabled: !canRerun,
            onClick: () => handleAction('rerun'),
            title: canRerun ? 'Rerun this job with same settings' : 'Can only rerun completed or failed jobs'
        }),
        // Stop button
        React.createElement(window.dash_blueprint_components.Button, {
            icon: 'stop',
            minimal: true,
            small: true,
            intent: 'danger',
            disabled: !isStoppable,
            onClick: () => handleAction('stop'),
        }),
        React.createElement(window.dash_blueprint_components.Button, {
            icon: 'search-template',
            minimal: true,
            small: true,
            intent: 'primary',
            onClick: () => handleAction('log'),
            title: 'Open LogViewer'
        }),
        React.createElement(window.dash_blueprint_components.Button, {
            icon: 'open-application',
            minimal: true,
            small: true,
            intent: 'primary',
            disabled: !isDone,
            onClick: () => handleAction('result'),
            title: 'Open ResultViewer'
        }),
        React.createElement(window.dash_blueprint_components.Button, {
            icon: 'trash',
            minimal: true,
            small: true,
            intent: 'danger',
            disabled: !isDeletable,
            onClick: () => handleAction('remove'),
            title: getRemoveButtonTitle(status)
        }),        
        React.createElement(window.dash_blueprint_components.Button, {
          icon: 'console',
          minimal: true,
          small: true,
          intent: 'primary',
          onClick: () => handleAction('terminal'),
          title: 'Open terminal in workspace'
        })
    ]);
};
```

## File: job_run/actions/log.py
```python
import os
import dash_ace
import dash_mantine_components as dmc
import dash_blueprint_components as dbpc
from pygtail import Pygtail
from dash import Input, Output, html, ALL, State, dcc, exceptions, ctx
from job_run.job_info import get_jobs_data
from utils.workspace import get_workspace_dir
from utils.logger import logger


class Log:
    def __init__(self, app):
        self.register_callbacks(app)

    def layout(self):
        return dmc.Paper(
            id="log-viewer-paper",
            children=[
                dmc.Grid(
                    [
                        # 왼쪽: 로그 파일 리스트
                        dmc.GridCol(
                            [
                                dmc.Paper(
                                    [
                                        dmc.Title("Log Files", order=4, mb=10, id="log-files-title"),
                                        html.Div(id="log-files-list"),
                                    ],
                                    p="md",
                                    withBorder=True,
                                )
                            ],
                            span=3,
                        ),
                        # 오른쪽: 로그 내용
                        dmc.GridCol(
                            [
                                dmc.Paper(
                                    [
                                        dmc.Group(
                                            [
                                                dmc.Title(
                                                    id="selected-log-title",
                                                    order=4,
                                                ),
                                            ],
                                            justify="space-around",
                                            mb=10,
                                        ),
                                        dash_ace.DashAceEditor(
                                            id="log-content-editor",
                                            theme="tomorrow",
                                            mode="text",
                                            tabSize=4,
                                            readOnly=True,
                                            style={
                                                "height": "60vh",
                                                "width": "100%",
                                            },
                                        ),
                                    ],
                                    p="md",
                                    withBorder=True,
                                )
                            ],
                            span=9,
                        ),
                    ],
                    gutter="md",
                ),
                # Store를 추가하여 현재 선택된 log file 정보를 저장
                # dcc.Interval(id="log-refresh-interval", interval=1000, disabled=True),
                dcc.Store(id="log-file-offset", data=None),
                dcc.Store(id="selected-log-file", data=None),
            ],
            style={"display": "None"},
        )

    def _find_log_files(self, root_dir):
        log_files = []
        try:
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    if not os.path.relpath(dirpath, root_dir).startswith("."):
                        if filename.endswith(".log") and not filename.startswith("."):
                            full_path = os.path.join(dirpath, filename)
                            rel_path = os.path.relpath(full_path, root_dir)
                            log_files.append(
                                {
                                    "path": full_path,
                                    "display_name": rel_path,
                                    "is_stdout": filename == "stdout.log",
                                }
                            )
            return sorted(log_files, key=lambda x: (not x["is_stdout"], x["display_name"]))
        except Exception as e:
            return []

    def _format_file_size(self, size_in_bytes):
        for unit in ["B", "KB", "MB", "GB"]:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.1f} TB"

    def read_log_content(self, log_path, offset=None):
        """로그 파일 읽기 - pygtail 사용"""
        try:
            if offset is None:
                # 처음 읽을 때는 전체 내용
                with open(log_path, "r") as f:
                    content = f.read()
                    return content, os.path.getsize(log_path)
            else:
                # 이후에는 새로운 내용만
                pygtail = Pygtail(log_path, offset=offset)
                new_content = "".join(pygtail.readlines())
                return new_content, pygtail.offset
        except Exception as e:
            logger.error(f"Error reading log file: {str(e)}")
            return None, None

    def read_new_content(self, file_path, offset):
        """파일의 새로운 내용만 읽기"""
        try:
            if not os.path.exists(file_path):
                return None, offset

            with open(file_path, "r") as f:
                # 이전 위치로 이동
                f.seek(offset)
                # 새로운 내용 읽기
                new_content = f.read()
                new_offset = f.tell()
                return new_content, new_offset
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return None, offset

    def register_callbacks(self, app):
        @app.callback(
            [
                Output("log-viewer-paper", "style", allow_duplicate=True),
                Output("log-files-list", "children", allow_duplicate=True),
                Output("selected-log-title", "children"),
                Output("log-content-editor", "value", allow_duplicate=True),
                Output("selected-log-file", "data"),
                Output("log-files-title", "children"),
            ],
            Input("job-table", "cellRendererData"),
            prevent_initial_call=True,
        )
        def show_log_viewer(data):

            if not data or data.get("value") != "log":
                return {"display": "none"}, [], "", "", None, ""
            try:
                row_id = data["rowId"]
                curr_jobs = get_jobs_data()
                job_names = [job["name"] for job in curr_jobs]
                job_name = job_names[int(row_id)]
                log_title = "Log Files: " + job_name

                job_details = [job["details"] for job in curr_jobs]
                job_detail = job_details[int(row_id)]
                job_app = None
                for p_v in job_detail:
                    if p_v["property"] == "APPLICATION":
                        job_app = p_v["value"]
                        break
                if not job_app:
                    return (
                        {"display": "block"},
                        [
                            dmc.Alert(
                                "Could not find application information for this job",
                                color="red",
                                variant="filled",
                            )
                        ],
                        "Error",
                        "Application information not found",
                        None,
                        log_title,
                    )

                app_dir = os.path.join(get_workspace_dir(), job_name, job_app)

                if not os.path.exists(app_dir):
                    logger.warning(f"Application directory not found: {app_dir}")
                    return (
                        {"display": "block"},
                        [
                            dmc.Stack(
                                [
                                    dmc.Alert(
                                        "Application directory not found",
                                        title="Directory Missing",
                                        color="orange",
                                        variant="filled",
                                    ),
                                    dmc.Text(
                                        f"Expected path: {app_dir}",
                                        size="sm",
                                        c="dimmed",
                                    ),
                                ],
                                gap="xs",
                            )
                        ],
                        "Directory Not Found",
                        "Application directory does not exist",
                        None,
                        log_title,
                    )

                log_files = self._find_log_files(app_dir)
                if not log_files:
                    return (
                        {"display": "block"},
                        [
                            dmc.Alert(
                                [
                                    dmc.Text(
                                        "No log files found in the application directory.",
                                        w=500,
                                    ),
                                    dmc.Text(
                                        "The job might have not generated any logs yet.",
                                        size="sm",
                                        c="dimmed",
                                    ),
                                ],
                                color="blue",
                                variant="light",
                            )
                        ],
                        "No Logs",
                        "No log files found",
                        None,
                        log_title,
                    )

                log_file_buttons = []
                for log_file in log_files:
                    log_file_buttons.append(
                        dbpc.Button(
                            log_file["display_name"],
                            icon="document",
                            id={
                                "type": "log-file-button",
                                "index": log_file["path"],
                            },
                            active=log_file["is_stdout"],
                            loading=False,
                            fill=True,
                        )
                    )

                default_log = next((log for log in log_files if log["is_stdout"]), log_files[0])
                content = ""
                selected_file_info = {
                    "path": default_log["path"],
                    "name": default_log["display_name"],
                }
                return ({"display": "block"}, log_file_buttons, f"Log: {default_log['display_name']}", content, selected_file_info, log_title)

            except Exception as e:
                logger.error(f"Error in show_log_viewer: {str(e)}")
                return (
                    {"display": "block"},
                    [
                        dmc.Alert(
                            [
                                dmc.Text(
                                    "An error occurred while trying to read the log files.",
                                    w=500,
                                ),
                                dmc.Text(str(e), size="sm", c="dimmed"),
                            ],
                            color="red",
                            variant="filled",
                        )
                    ],
                    "Error",
                    f"Error: {str(e)}",
                    None,
                    log_title,
                )

        # @app.callback(
        #     [
        #         Output("auto-refresh-log", "disabled"),
        #         Output("log-refresh-interval", "disabled"),
        #     ],
        #     Input("selected-log-file", "data"),
        # )
        # def toggle_auto_refresh(selected_file):
        #     """선택된 파일이 있을 때만 auto refresh 활성화"""
        #     disabled = selected_file is None
        #     return disabled, disabled

        @app.callback(
            [
                Output("log-content-editor", "value", allow_duplicate=True),
                Output("log-file-offset", "data"),
            ],
            [
                Input("auto-refresh-interval", "n_intervals"),
                Input("manual-refresh", "n_clicks"),
            ],
            [
                State("selected-log-file", "data"),
                State("log-file-offset", "data"),
                State("auto-refresh-switch", "checked"),
                State("log-content-editor", "value"),
            ],
            prevent_initial_call=True,
        )
        def update_log_content(n_intervals, n_clicks, selected_file, offset, auto_refresh, current_content):
            """로그 내용 업데이트"""
            if not selected_file:
                raise exceptions.PreventUpdate

            ctx_triggered = ctx.triggered_id
            log_path = selected_file["path"]

            if ctx_triggered == "manual-refresh":
                # 수동 새로고침 - 전체 내용 다시 읽기
                with open(log_path, "r") as f:
                    content = f.read()
                    return content, f.tell()

            elif ctx_triggered == "auto-refresh-interval" and auto_refresh:
                # 자동 새로고침 - 새로운 내용만 읽기
                new_content, new_offset = self.read_new_content(log_path, offset)
                if new_content:
                    return current_content + new_content, new_offset
            raise exceptions.PreventUpdate

        @app.callback(
            [
                Output("selected-log-title", "children", allow_duplicate=True),
                Output("log-content-editor", "value", allow_duplicate=True),
                Output("selected-log-file", "data", allow_duplicate=True),
                Output("log-file-offset", "data", allow_duplicate=True),
                Output({"type": "log-file-button", "index": ALL}, "active"),
                Output({"type": "log-file-button", "index": ALL}, "loading"),
            ],
            Input({"type": "log-file-button", "index": ALL}, "n_clicks"),
            State({"type": "log-file-button", "index": ALL}, "id"),
            prevent_initial_call=True,
        )
        def select_log_file(clicks, button_ids):

            if not any(clicks):
                raise exceptions.PreventUpdate

            selected_ctx = ctx.triggered_id
            selected_idx = next(
                (i for i, d in enumerate(button_ids) if d["index"] == selected_ctx["index"]),
                None,
            )

            log_path = selected_ctx["index"]
            log_name = os.path.basename(log_path)

            try:
                file_size = os.path.getsize(log_path)
                max_size = 10 * 1024 * 1024  # 10MB

                if file_size > max_size:
                    with open(log_path, "rb") as f:
                        f.seek(max(file_size - max_size, 0))
                        if file_size > max_size:
                            f.readline()
                        content = f.read().decode("utf-8", errors="replace")
                    warning_msg = "\n\n[WARNING: File too large, showing last 10MB only...]\n\n"
                    content = warning_msg + content

                else:
                    with open(log_path, "r") as f:
                        content = f.read()

                selected_file_info = {"path": log_path, "name": log_name}
                active_states = [i == selected_idx for i in range(len(button_ids))]

                size_str = self._format_file_size(file_size)
                return (
                    f"Log: {log_name} ({size_str})",
                    content,
                    selected_file_info,
                    file_size,
                    active_states,
                    [False] * len(button_ids),
                )
            except Exception as e:
                return (
                    "Error",
                    f"Could not read log file: {str(e)}",
                    None,
                    None,
                    [False] * len(button_ids),
                    [False] * len(button_ids),
                )
```

## File: job_run/actions/remove.py
```python
import os
import shutil
import dash_blueprint_components as dbpc
from datetime import datetime
from dash import Input, Output, no_update, ALL, MATCH, State, html, dcc
from utils.workspace import get_workspace_dir
from utils.logger import logger
from job_run.job_info import get_jobs_data


class Remove:
    def __init__(self, app):
        self.register_callbacks(app)

    def layout(self):
        return html.Div(
            [
                dbpc.Alert(
                    id="remove-job-alert",
                    icon="trash",
                    intent="danger",
                    isOpen=False,
                    children="",
                    cancelButtonText="Cancel",
                    confirmButtonText="Remove",
                ),
                dcc.Store(id="selected-remove-job-info", data=None),
            ]
        )

    def remove_job(self, job_name):
        try:
            logger.info("remove_job")
            # 작업 디렉토리 경로
            job_dir = os.path.join(get_workspace_dir(), job_name)
            if not os.path.exists(job_dir):
                return False, f"Job directory not found: {job_name}"
            # 압축 파일명 생성 (.archived_JOB_NAME_TIMESTAMP.tar.gz)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f".archived_{job_name}_{timestamp}.tar.gz"
            archive_path = os.path.join(get_workspace_dir(), archive_name)
            # 디렉토리 tar.gz로 압축
            # with tarfile.open(archive_path, "w:gz") as tar:
            #     tar.add(job_dir, arcname=os.path.basename(job_dir))
            # 원본 디렉토리 삭제
            logger.info(f"remove_job: {job_dir}")
            shutil.rmtree(job_dir)
            logger.info(f"Successfully archived job {job_name} to {archive_name}")
            return True, "Job archived successfully"
        except Exception as e:
            logger.error(f"Error archiving job {job_name}: {str(e)}")
            return False, str(e)

    def register_callbacks(self, app):
        @app.callback(
            Output("job-table", "rowData", allow_duplicate=True),
            Output("remove-job-alert", "isConfirmed"),
            Output("remove-job-alert", "isCanceled"),
            Input("remove-job-alert", "isConfirmed"),
            State("selected-remove-job-info", "data"),
            prevent_initial_call=True,
        )
        def handle_remove_confirmation(confirmed, selected_job):
            print("handle_remove_confirmation")
            print(f"selected_job: {selected_job}")

            """ remove 확인 후 작업 처리"""
            if not confirmed or not selected_job or selected_job.get("action") != "remove":
                return no_update, False, False

            job_name = selected_job["job_name"]
            print(f"job_name: {job_name}")
            # 작업 remove
            success, message = self.remove_job(job_name)
            print(f"message: {message}")
            if not success:
                logger.error(f"Failed to remove job {job_name}: {message}")
                return no_update, False, False
            logger.info(f"Successfully remove job {job_name}")
            current_data = get_jobs_data()
            return current_data, False, False

        @app.callback(
            Output("remove-job-alert", "isOpen", allow_duplicate=True),
            Output("remove-job-alert", "children", allow_duplicate=True),
            Output("selected-remove-job-info", "data", allow_duplicate=True),
            Input("job-table", "cellRendererData"),
            prevent_initial_call=True,
        )
        def show_remove_confirmation(data):
            """remove 확인 Alert 표시"""
            if not data or data.get("value") == "remove":
                row_id = data["rowId"]
                curr_jobs = get_jobs_data()
                job_names = [job["name"] for job in curr_jobs]

                if not job_names or int(row_id) >= len(job_names):
                    return False, "", None

                job_name = job_names[int(row_id)]

                # job status 확인
                job_status = curr_jobs[int(row_id)]["status"]
                if job_status in ["running", "pending"]:
                    logger.warning(f"Cannot remove job {job_name} in {job_status} status")
                    return False, "", None

                return (
                    True,
                    f"Are you sure you want to remove the job '{job_name}'?",
                    {"job_name": job_name, "action": "remove"},
                )

            else:
                return False, "", None
```

## File: job_run/actions/rerun.py
```python
import os
import yaml
import json
import dash_blueprint_components as dbpc
from dash import Input, Output, State, no_update, html, dcc, ctx, set_props
from utils.logger import logger
from utils.workspace import get_workspace_dir
from utils.settings import DISK_CACHE
from job_run.job_info import get_jobs_data


class Rerun:
    def __init__(self, app):
        self.register_callbacks(app)
        self.queue_backup_file = os.path.join(DISK_CACHE, f"queue_data.json")

    def layout(self):
        return dbpc.OverlayToaster(id="rerun-toaster", position="top-right", usePortal=True)

    def load_job_config(self, job_name):
        try:
            config_path = os.path.join(get_workspace_dir(), job_name, "job_config.yaml")
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading job config for {job_name}: {str(e)}")
            return None

    def update_queue_backup(self, job_config):
        """작업 설정을 JobQueue 백업 파일에 추가"""
        try:
            # 백업 파일 로드
            queue_data = {"rowData": [], "columnDefs": []}
            if os.path.exists(self.queue_backup_file):
                with open(self.queue_backup_file, "r") as f:
                    try:
                        queue_data = json.load(f)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in queue backup file. Creating new backup.")

            # 작업 데이터 생성
            job_data = self.create_queue_job_data(job_config)

            # 새 작업을 rowData에 추가
            if job_data:
                row_data = queue_data.get("rowData", [])
                row_data.append(job_data)
                queue_data["rowData"] = row_data

                # 컬럼 정의가 비어있으면 생성
                if not queue_data.get("columnDefs"):
                    queue_data["columnDefs"] = self.create_column_defs(job_data)

                # 백업 파일 저장
                with open(self.queue_backup_file, "w") as f:
                    json.dump(queue_data, f)

                logger.info(f"Job {job_config['name']} added to queue backup file")
                return True

            return False
        except Exception as e:
            logger.error(f"Error updating queue backup: {str(e)}")
            return False

    def create_queue_job_data(self, job_config):
        """작업 설정에서 Queue 테이블용 데이터 생성"""
        try:
            # 기본 데이터 설정
            job_data = {
                "_id": os.urandom(16).hex(),  # 고유 ID 생성
                "APPLICATION": job_config["app"],
                "JOBNAME": job_config["name"],
            }

            # PVT 코너 정보 추가
            if job_config.get("corners"):
                corner = job_config["corners"]
                job_data.update(
                    {
                        "PROCESS": corner.get("PROCESS", ""),
                        "VOLTAGE": corner.get("VOLTAGE", ""),
                        "TEMPERATURE": corner.get("TEMPERATURE", ""),
                    }
                )

            # 입력값 추가
            for key, value in job_config.get("inputs", {}).items():
                job_data[key] = value

            return job_data
        except Exception as e:
            logger.error(f"Error creating queue job data: {str(e)}")
            return None

    def create_column_defs(self, job_data):
        """Queue 테이블용 컬럼 정의 생성"""
        try:
            column_defs = [{"field": "_id", "hide": True, "suppressExport": True}]

            # 기본 컬럼 추가
            column_defs.append(
                {
                    "field": "APPLICATION",
                    "headerName": "APPLICATION",
                    "pinned": "left",
                    "checkboxSelection": True,
                    "headerCheckboxSelection": True,
                }
            )
            column_defs.append({"field": "JOBNAME", "headerName": "JOBNAME", "pinned": "left"})

            # PVT 컬럼 추가
            pvt_columns = ["PROCESS", "VOLTAGE", "TEMPERATURE"]
            for col in pvt_columns:
                if col in job_data:
                    column_defs.append({"field": col, "headerName": col})

            # 나머지 필드 추가
            for field in job_data.keys():
                if field not in ["_id", "APPLICATION", "JOBNAME", "PROCESS", "VOLTAGE", "TEMPERATURE"]:
                    column_defs.append({"field": field, "headerName": field})

            return column_defs
        except Exception as e:
            logger.error(f"Error creating column definitions: {str(e)}")
            return []

    def register_callbacks(self, app):
        @app.callback(
            Output("rerun-toaster", "toasts", allow_duplicate=True),
            Output("job-rerun-alert", "isOpen"),
            Output("job-rerun-alert", "children"),
            Input("job-table", "cellRendererData"),
            prevent_initial_call=True,
        )
        def show_rerun_confirmation(data):
            """Rerun 확인 및 Queue 백업 업데이트"""
            if not data or data.get("value") != "rerun":
                return None, False, ""

            try:
                row_id = data["rowId"]
                curr_jobs = get_jobs_data()
                job_names = [job["name"] for job in curr_jobs]

                if not job_names or int(row_id) >= len(job_names):
                    return None, False, ""

                job_name = job_names[int(row_id)]
                job_config = self.load_job_config(job_name)

                if not job_config:
                    return (
                        [
                            dbpc.Toast(
                                message="Failed to load job configuration",
                                intent="error",
                                icon="error",
                            )
                        ],
                        False,
                        "",
                    )

                # JobQueue 백업 파일 업데이트
                success = self.update_queue_backup(job_config)

                if success:
                    alert_message = f"Job '{job_name}' has been added to the Queue in Set Page"
                    return (
                        [
                            dbpc.Toast(
                                message="Job added to Queue in Set Page",
                                intent="success",
                                icon="tick",
                            )
                        ],
                        True,
                        alert_message,
                    )
                else:
                    return (
                        [
                            dbpc.Toast(
                                message="Failed to add job to Queue",
                                intent="error",
                                icon="error",
                            )
                        ],
                        False,
                        "",
                    )

            except Exception as e:
                logger.error(f"Error in rerun callback: {str(e)}")
                return (
                    [
                        dbpc.Toast(
                            message=f"Unexpected error: {str(e)}",
                            intent="error",
                            icon="error",
                        )
                    ],
                    False,
                    "",
                )
```

## File: job_run/actions/result.py
```python
import os
import subprocess
from dash import Input, Output, no_update, exceptions
from utils.logger import logger
from job_run.job_info import get_jobs_data
import dash_mantine_components as dmc
from utils.workspace import get_workspace_dir


class Result:
    def __init__(self, app):
        self.register_callbacks(app)

    def layout(self):
        return dmc.Modal(
            id="result-error-modal",
            centered=True,
            zIndex=1000,
            children=[dmc.Text(id="result-error-message", size="sm", c="red", w=500)],
        )

    def open_result_file(self, job_name, job_app):
        try:

            result_path = os.path.join(get_workspace_dir(), job_name, job_app, "RESULT", "result.csv")
            if not os.path.exists(result_path):
                return False, f"Result file not found: {result_path}"
            cmd = f"sorv_sub {result_path}"
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            _, stderr = process.communicate()
            if process.returncode != 0:
                return False, f"Failed to open ResultViewer: {stderr.decode()}"
            return True, "Successfully opened ResultViewer"
        except Exception as e:
            return False, str(e)

    def register_callbacks(self, app):
        @app.callback(
            Output("result-error-modal", "opened"),
            Output("result-error-message", "opened"),
            Input("job-table", "cellRendererData"),
            prevent_initial_call=True,
        )
        def handle_result_button(data):

            if not data or data.get("value") != "result":
                raise exceptions.PreventUpdate
            try:
                row_id = data["rowId"]
                current_data = get_jobs_data()
                job = current_data[int(row_id)]
                job_app = None
                for detail in job["details"]:
                    if detail["property"] == "APPLICATION":
                        job_app = detail["value"]
                        break
                if not job_app:
                    return True, "Could not find application information"
                success, message = self.open_result_file(job_name, job_app)
                if not success:
                    return True, message
                return Faluse, ""

            except Exception as e:
                logger.error(f"Error handling result button: {str(e)}")
                return True, f"Unexpected error: {str(e)}"
```

## File: job_run/actions/stop.py
```python
import os
import yaml
import signal
import dash_blueprint_components as dbpc
from datetime import datetime
from dash import Input, Output, no_update, State, html, dcc
from utils.logger import logger
from utils.workspace import get_workspace_dir
from utils.lsf import get_lsf_jobs, kill_lsf_jobs
from job_run.job_info import is_job_stoppable, get_jobs_data


class Stop:
    def __init__(self, app):
        self.register_callbacks(app)

    def layout(self):
        return html.Div(
            [
                dbpc.Alert(
                    id="stop-job-alert",
                    icon="stop",
                    intent="danger",
                    isOpen=False,
                    children="",
                    cancelButtonText="Cancel",
                    confirmButtonText="Stop",
                ),
                dcc.Store(id="selected-stop-job-info", data=None),
            ]
        )

    def stop_job(self, job_name):
        """작업 중지"""
        try:
            # 1. job_config.yaml 읽기
            job_dir = os.path.join(get_workspace_dir(), job_name)
            config_path = os.path.join(job_dir, "job_config.yaml")

            with open(config_path) as f:
                job_config = yaml.safe_load(f)

            # 상태 확인
            if not is_job_stoppable(job_config["status"]):
                return False, f"Cannot stop job in {job_config['status']} status"

            # running 상태일 경우 프로세스 종료
            if job_config["status"] == "running":
                pid = job_config.get("pid")
                if pid:
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGTERM)
                    except ProcessLookupError:
                        logger.warning(f"Process {pid} not found, job may have already terminated")
                    except Exception as e:
                        logger.error(f"Error stopping process {pid}: {str(e)}")
                        return False, f"Failed to stop process: {str(e)}"

            lsf_jobs = get_lsf_jobs(user_name=os.getenv("USER"))
            kill_job_ids = []
            for lsf_job in lsf_jobs:
                if lsf_job.get("cwd") == os.path.join(job_dir, job_config.get("app")):
                    if lsf_job["job_status"] != "DONE":
                        kill_job_ids.append(lsf_job["job_id"])
            if kill_job_ids:
                kill_lsf_jobs(kill_job_ids)

            # job_config 업데이트
            job_config.update(
                {
                    "status": "failed",
                    "message": "Job stopped by user",
                    "job_finish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

            with open(config_path, "w") as f:
                yaml.dump(job_config, f)

            return True, "Job stopped successfully"

        except Exception as e:
            logger.error(f"Error stopping job {job_name}: {str(e)}")
            return False, str(e)

    def register_callbacks(self, app):
        @app.callback(
            Output("stop-job-alert", "isOpen", allow_duplicate=True),
            Output("stop-job-alert", "children", allow_duplicate=True),
            Output("selected-stop-job-info", "data", allow_duplicate=True),
            Input("job-table", "cellRendererData"),
            prevent_initial_call=True,
        )
        def show_stop_confirmation(data):
            """중지 확인 Alert 표시"""
            if not data or data.get("value") == "stop":
                row_id = data["rowId"]
                curr_jobs = get_jobs_data()
                job_names = [job["name"] for job in curr_jobs]

                if not job_names or int(row_id) >= len(job_names):
                    return False, "", None

                job_name = job_names[int(row_id)]

                # job status 확인
                job_status = curr_jobs[int(row_id)]["status"]

                if not is_job_stoppable(job_status):
                    logger.warning(f"Cannot stop job {job_name} in {job_status} status")
                    return False, "", None
                return (
                    True,
                    f"Are you sure you want to stop the job '{job_name}'?",
                    {"job_name": job_name, "action": "stop"},
                )
            return False, "", None

        @app.callback(
            Output("job-table", "rowData", allow_duplicate=True),
            Output("stop-job-alert", "isConfirmed"),
            Output("stop-job-alert", "isCanceled"),
            Input("stop-job-alert", "isConfirmed"),
            State("selected-stop-job-info", "data"),
            prevent_initial_call=True,
        )
        def handle_stop_confirmation(confirmed, selected_job):
            """중지 확인 후 작업 처리"""
            if not confirmed or not selected_job or selected_job.get("action") != "stop":
                return no_update, False, False
            job_name = selected_job["job_name"]
            # 작업 중지
            success, message = self.stop_job(job_name)
            if not success:
                logger.error(f"Failed to stop job {job_name}: {message}")
                # TODO: 에러 알림 표시
                return no_update, False, False
            logger.info(f"Successfully stopped job {job_name}")
            jobs = get_jobs_data()
            return jobs, False, False
```

## File: job_run/actions/terminal.py
```python
import os
import subprocess
import dash_blueprint_components as dbpc
from dash import Input, Output, exceptions, no_update
from utils.logger import logger
from job_run.job_info import get_jobs_data


class Terminal:
    def __init__(self, app):
        self.register_callbacks(app)

    def layout(self):
        return dbpc.OverlayToaster(id="terminal-toaster", position="top-right", usePortal=True)

    def register_callbacks(self, app):
        @app.callback(
            Output("terminal-toaster", "toasts", allow_duplicate=True),
            Input("job-table", "cellRendererData"),
            prevent_initial_call=True,
        )
        def handle_terminal_button(data):
            if not data or data.get("value") != "terminal":
                raise exceptions.PreventUpdate
            try:
                row_id = data["rowId"]
                current_data = get_jobs_data()
                name = current_data[int(row_id)]["name"]
                for d in current_data[int(row_id)]["details"]:
                    if d["property"] == "APPLICATION":
                        app = d["value"]
                    if d["property"] == "Workspace":
                        job_workspace = d["value"]
                cshell_command = f"/user/signoff.dev/deepwonwoo/scripts/launcher_terminal {os.environ.get('DISPLAY')} {name}"
                subprocess.Popen(
                    ["csh", "-c", cshell_command],
                    cwd=os.path.join(job_workspace, app),
                    env=os.environ,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                return [
                    dbpc.Toast(
                        message=f"Opened terminal in workspace: {job_workspace}",
                        intent="success",
                        icon="tick",
                    )
                ]
            except Exception as e:
                return [
                    dbpc.Toast(
                        message=f"Error opening terminal: {str(e)}",
                        intent="error",
                        icon="error",
                    )
                ]
```

## File: job_run/job_info.py
```python
import os
import yaml
import traceback
from utils.workspace import get_workspace_dir
from utils.lsf import get_lsf_jobs
from utils.logger import logger


def get_jobs_data():
    jobs = []
    for job_name in os.listdir(get_workspace_dir()):
        job_dir = os.path.join(get_workspace_dir(), job_name)
        if not os.path.isdir(job_dir):
            continue
        config_path = os.path.join(job_dir, "job_config.yaml")
        if not os.path.exists(config_path):
            continue
        with open(config_path) as f:
            config = yaml.safe_load(f)
            status = config.get("status", "pending")
            job = {
                "name": config.get("name", job_name),
                "owner": config.get("owner"),
                "status": status,
                "message": config.get("message", ""),
                "job_start_time": config.get("job_start_time"),
                "job_finish_time": config.get("job_finish_time"),
            }  # 기본 table에 표시될 정보
            job["details"] = [
                {"property": "APPLICATION", "value": config.get("app")},
                {"property": "Workspace", "value": config.get("workspace")},
            ]  # Detail table에 표시될 job config 정보
            inputs = config.get("inputs", {})  # status 정규화 - 대문자로 통일
            for key, value in inputs.items():
                job["details"].append({"property": f"Input: {key}", "value": value})
            corners = config.get("corners", {})  # Corners 정보 추가
            if corners:
                corner_str = f"Process: {corners.get('process', '')}, "
                corner_str += f"Voltage: {corners.get('voltage', '')}, "
                corner_str += f"Temperature: {corners.get('temperature', '')}"
                job["details"].append({"property": f"Corner", "value": corner_str})
            lsf_jobs = get_lsf_jobs(user_name=os.getenv("USER"))
            for lsf_job in lsf_jobs:  # Add lsf job info
                if lsf_job.get("cwd") == os.path.join(job_dir, config.get("app")):
                    job["details"].append(
                        {
                            "property": f"LSF Job Id: {lsf_job['job_id']}",
                            "value": f"status: {lsf_job['job_status']}, runTime: {lsf_job['runTime']}",
                        }
                    )
            jobs.append(job)
    return jobs


def is_job_stoppable(status):
    return status in ["running", "pending"]


def is_job_restartable(status):
    return status in ["done", "failed"]
```

## File: job_run/jobFiltering.py
```python
import dash_mantine_components as dmc
import dash_blueprint_components as dbpc
from utils.logger import logger

from dash import Input, Output, State, ctx, no_update, ctx


class FilteringBtns:
    def __init__(self, app):
        self.register_callbacks(app)

    def layout(self):
        return dmc.Group(
            [
                dbpc.ButtonGroup(
                    [
                        dbpc.Button(
                            "All",
                            id="filter-status-all",
                            outlined=True,
                            intent="primary",
                            small=True,
                            rightIcon=dmc.Badge("0", variant="filled", size="xs", color="blue"),
                            active=True,
                        ),
                        dbpc.Button(
                            "Pending",
                            id="filter-status-pending",
                            outlined=True,
                            small=True,
                            rightIcon=dmc.Badge("0", variant="filled", size="xs", color="yellow"),
                        ),
                        dbpc.Button(
                            "Running",
                            id="filter-status-running",
                            intent="success",
                            outlined=True,
                            small=True,
                            rightIcon=dmc.Badge("0", variant="filled", size="xs", color="green"),
                        ),
                        dbpc.Button(
                            "Done",
                            id="filter-status-done",
                            intent="primary",
                            outlined=True,
                            small=True,
                            rightIcon=dmc.Badge("0", variant="filled", size="xs", color="indigo"),
                        ),
                        dbpc.Button(
                            "Failed",
                            id="filter-status-failed",
                            intent="danger",
                            outlined=True,
                            small=True,
                            rightIcon=dmc.Badge("0", variant="filled", size="xs", color="red"),
                        ),
                    ]
                ),
                dmc.TextInput(
                    id="search-job",
                    placeholder="Search jobs...",
                    size="xs",
                    leftSection=dbpc.Icon(icon="search"),
                    style={"width": 200},
                ),
            ],
            justify="space-around",
        )

    def register_callbacks(self, app):
        @app.callback(
            Output("job-table", "filterModel"),
            Output("filter-status-all", "active"),
            Output("filter-status-pending", "active"),
            Output("filter-status-running", "active"),
            Output("filter-status-done", "active"),
            Output("filter-status-failed", "active"),
            Input("filter-status-all", "n_clicks"),
            Input("filter-status-pending", "n_clicks"),
            Input("filter-status-running", "n_clicks"),
            Input("filter-status-done", "n_clicks"),
            Input("filter-status-failed", "n_clicks"),
            Input("search-job", "value"),
            State("job-table", "filterModel"),
            prevent_initial_call=True,
        )  # 검색 input 추가  # 현재 필터 상태 가져오기
        def update_filter(
            all_clicks,
            pending_clicks,
            running_clicks,
            done_clicks,
            failed_clicks,
            search_value,
            current_filter,
        ):
            if not ctx.triggered:
                return no_update, no_update, no_update, no_update, no_update, no_update
            button_id = ctx.triggered_id
            button_states = {
                "filter-status-all": False,
                "filter-status-pending": False,
                "filter-status-running": False,
                "filter-status-done": False,
                "filter-status-failed": False,
            }
            if button_id in button_states:
                button_states[button_id] = True
            if button_id == "search-job":
                new_filter_model = {}
                if current_filter and "name" in current_filter:
                    new_filter_model["name"] = current_filter["name"]
                if search_value:
                    new_filter_model["name"] = {
                        "filterType": "text",
                        "type": "contains",
                        "filter": search_value,
                    }
                else:
                    new_filter_model["name"] = {}
                if current_filter and "status" in current_filter:
                    new_filter_model["status"] = current_filter["status"]
                return (new_filter_model, *button_states.values())
            elif button_id == "filter-status-all":
                return ({}, *button_states.values())
            status_map = {
                "filter-status-pending": "pending",
                "filter-status-running": "running",
                "filter-status-done": "done",
                "filter-status-failed": "failed",
            }
            if button_id in status_map:
                filter_model = {
                    "status": {
                        "filterType": "agSetColumnFilter",
                        "values": [status_map[button_id]],
                    }
                }
                return (filter_model, *button_states.values())
            return (no_update, *button_states.values())

        @app.callback(
            Output("filter-status-all", "rightIcon"),
            Output("filter-status-pending", "rightIcon"),
            Output("filter-status-running", "rightIcon"),
            Output("filter-status-done", "rightIcon"),
            Output("filter-status-failed", "rightIcon"),
            Input("job-table", "rowData"),
            prevent_initial_call=True,
        )
        def update_status_counts(data):
            def create_badge(count, c="grey"):
                return dmc.Badge(str(count), variant="filled", size="xs", color=c)

            if not data:
                default_badge = lambda: dmc.Badge("0", variant="filled", size="xs", color="grey")
                return (
                    default_badge(),
                    default_badge(),
                    default_badge(),
                    default_badge(),
                    default_badge(),
                )
            status_counts = {
                "all": len(data),
                "pending": 0,
                "running": 0,
                "done": 0,
                "failed": 0,
            }
            for row in data:
                status = row.get("status", "").lower()
                if status in status_counts:
                    status_counts[status] += 1
            return (
                create_badge(status_counts["all"], "blue"),
                create_badge(status_counts["pending"], "yellow"),
                create_badge(status_counts["running"], "green"),
                create_badge(status_counts["done"], "indigo"),
                create_badge(status_counts["failed"], "red"),
            )
```

## File: job_run/jobMonitoring.py
```python
import os
import subprocess
import dash_blueprint_components as dbpc
import dash_mantine_components as dmc
from datetime import datetime
from utils.logger import logger
from dash import Input, Output, State, ctx, no_update, ctx, dcc
from job_run.job_info import get_jobs_data
from utils.workspace import get_job_count


class Monitoring:
    def __init__(self, app):
        self.register_callbacks(app)

    def layout(self):
        return dmc.Group(
            [
                dmc.Switch(
                    id="auto-refresh-switch",
                    label="Auto-refresh",
                    size="sm",
                    checked=True,
                ),
                dbpc.Button(id="manual-refresh", icon="refresh", outlined=True, loading=False),
                dmc.Text(id="last-refresh-time", size="xs", c="dimmed"),
                dcc.Interval(id="auto-refresh-interval", interval=10 * 1000, disabled=False),
                dcc.Store(id="previous-data-store"),
            ]
        )

    def lsf_btn(self):
        return dbpc.Button("LSF Job Monitoring", id="lsf-job-monitoring-btn", icon="graph", small=True)

    def _compare_data(self, current_data, previous_data):
        if len(current_data) != len(previous_data):
            return True

        for curr_job in current_data:
            job_name = curr_job["name"]
            prev_job = next((job for job in previous_data if job["name"] == job_name), None)

            if prev_job is None:
                return True

            if curr_job.get("status") != prev_job.get("status"):
                return True

            if len(curr_job.get("details")) != len(prev_job.get("details")):
                return True
            if set(frozenset(d.items()) for d in curr_job.get("details")) != set(frozenset(d.items()) for d in prev_job.get("details")):
                return True

        return False

    def register_callbacks(self, app):
        @app.callback(
            Output("auto-refresh-interval", "disabled"),
            Input("auto-refresh-switch", "checked"),
            prevent_initial_call=True,
        )
        def toggle_auto_refresh(checked):
            return False if checked else True

        @app.callback(
            Output("job-table", "rowData"),
            Output("manual-refresh", "loading"),
            Output("last-refresh-time", "children"),
            Output("previous-data-store", "data"),
            Output("workspace-display-indicator", "label", allow_duplicate=True),
            Input("manual-refresh", "n_clicks"),
            Input("auto-refresh-interval", "n_intervals"),
            State("previous-data-store", "data"),
            State("job-table", "filterModel"),
        )
        def refresh_table(manual_clicks, auto_intervals, previous_data, filter_model):
            triggered_id = ctx.triggered_id
            try:
                current_data = get_jobs_data()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if previous_data:
                    has_changes = self._compare_data(current_data, previous_data)
                    if not has_changes:
                        return (
                            no_update,
                            False,
                            f"Last refresh: {current_time}",
                            previous_data,
                            str(get_job_count()),
                        )

                return (
                    current_data,
                    False,
                    f"Last refresh: {current_time}",
                    current_data,
                    str(get_job_count()),
                )

            except Exception as e:
                logger.error(f"refresh_table error:{e}")
                return no_update, False, no_update, previous_data, str(get_job_count())

        @app.callback(
            Output("lsf-job-monitoring-btn", "n_clicks"),
            Input("lsf-job-monitoring-btn", "n_clicks"),
            prevent_initial=True,
        )
        def open_monitoring_page(n_clicks):
            if n_clicks:
                try:
                    user_name = os.getenv("USER")
                    url = f"https://grafana/signoff-launcher?orgId=1&var-user_name={user_name}"
                    chrome_path = "/user/signoff.dev/deepwonwoo/SW/chromium/chrome"
                    subprocess.Popen(
                        [
                            chrome_path,
                            "--no-sandbox",
                            "--ignore-certificate-errors",
                            url,
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                except Exception as e:
                    logger.error(f"failed to open monitoring page: {e}")

            return 0
```

## File: job_run/jobTable.py
```python
import dash_ag_grid as dag
from dash import html, dcc
from job_run.actions.result import Result
from job_run.actions.rerun import Rerun
from job_run.actions.remove import Remove
from job_run.actions.log import Log
from job_run.actions.stop import Stop
from job_run.actions.terminal import Terminal


class JobTable:
    def __init__(self, app):
        # self.rerun_action = Rerun(app)
        self.stop_action = Stop(app)
        self.log_action = Log(app)
        self.result_action = Result(app)
        self.remove_action = Remove(app)
        self.terminal_action = Terminal(app)

    def layout(self):
        defaultColDef = {"resizable": True, "sortable": True, "filter": True}
        detailColumnDefs = [
            {"headerName": "Property", "field": "property", "flex": 1},
            {"headerName": "Value", "field": "value", "flex": 3},
        ]
        columnDefs = [
            {
                "headerName": "Job Name",
                "field": "name",
                "filter": "agTextColumnFilter",
                "cellRenderer": "agGroupCellRenderer",
                "minWidth": 380,
            },
            {
                "headerName": "Actions",
                "field": "actions",
                "cellRenderer": "ActionButtons",
                "sortable": False,
                "filter": False,
                "minWidth": 200,
            },
            {
                "headerName": "Status",
                "field": "status",
                "cellRenderer": "StatusIndicator",
                "flex": 1,
            },
            {"headerName": "Message", "field": "message", "minWidth": 100, "flex": 2},
            {
                "headerName": "Owner",
                "field": "owner",
                "valueFormatter": {"function": "value === null ? '-' : value"},
                "flex": 1,
            },
            {
                "headerName": "Start Time",
                "field": "job_start_time",
                "valueFormatter": {"function": "params.data.job_start_time ? d3.timeFormat('%m/%d %H:%M:%S')(d3.timeParse('%Y-%m-%d %H:%M:%S')(params.data.job_start_time)) : '' "},
                "flex": 1,
            },
            {
                "headerName": "Finish Time",
                "field": "job_finish_time",
                "valueFormatter": {
                    "function": "params.data.job_finish_time ? d3.timeFormat('%m/%d %H:%M:%S')(d3.timeParse('%Y-%m-%d %H:%M:%S')(params.data.job_finish_time)) : '' "
                },
                "flex": 1,
            },
        ]
        dashGridOptions = {
            "rowHeight": 35,
            "suppressCellFocus": True,
            "animateRows": True,
            "pagination": True,
            "paginationAutoPageSize": True,
        }
        return html.Div(
            [
                dag.AgGrid(
                    id="job-table",
                    rowData=[],
                    columnSize="sizeToFit",
                    columnDefs=columnDefs,
                    defaultColDef=defaultColDef,
                    dashGridOptions=dashGridOptions,
                    masterDetail=True,
                    detailCellRendererParams={
                        "detailGridOptions": {
                            "headerHeight": 0,
                            "rowHeight": 25,
                            "columnDefs": detailColumnDefs,
                            "defaultColDef": defaultColDef,
                        },
                        "detailColName": "details",
                        "suppressCallback": True,
                    },
                    enableEnterpriseModules=True,
                    style={"height": "600px", "width": "100%"},
                    className="ag-theme-alpine",
                ),
                # self.rerun_action.layout(),
                self.stop_action.layout(),
                self.log_action.layout(),
                self.result_action.layout(),
                self.remove_action.layout(),
                self.terminal_action.layout(),
            ]
        )
```

## File: job_run/page.py
```python
import dash_mantine_components as dmc
from job_run.jobTable import JobTable
from job_run.jobFiltering import FilteringBtns
from job_run.jobMonitoring import Monitoring


class RunPage:
    def __init__(self, app):
        self.job_table = JobTable(app)
        self.job_filtering_btns = FilteringBtns(app)
        self.job_monitoring = Monitoring(app)

    def layout(self):
        return dmc.Container(
            children=[
                dmc.Paper(
                    children=[
                        dmc.Group(
                            [
                                dmc.Title("Job Runs", order=2),
                                self.job_monitoring.lsf_btn(),
                            ],
                            justify="space-between",
                        ),
                        dmc.Space(h=10),
                        dmc.Group(
                            [
                                self.job_filtering_btns.layout(),
                                self.job_monitoring.layout(),
                            ],
                            justify="space-between",
                            my="md",
                        ),
                        self.job_table.layout(),
                    ],
                    p="lg",
                    shadow="xs",
                    withBorder=True,
                )
            ],
            size="xl",
            fluid=True,
        )
```

## File: job_set/jobCards.py
```python
import json
import uuid
import yaml
import dash_mantine_components as dmc
import dash_blueprint_components as dbpc
from dash import Input, Output, State, Patch, ALL, MATCH, ctx, exceptions, html, no_update, dcc
from utils.settings import SIGNOFF_APPLICATION_YAML
from utils.logger import logger
from utils.manual_link import TOOL_MANUAL_MAP
from utils.sol_constants import IDENTIFIER


class JobCards:
    def __init__(self, app, config_loader):
        self.app = app
        self.MAX_PVT_CORNERS = 5
        self.MIN_PVT_CORNERS = 1
        self.config_loader = config_loader
        self.app_configs = config_loader.app_configs
        self.classification_schemes = config_loader.get_classification_schemes()
        self.logger = logger
        self._register_callbacks(app)

    def create_job_card(self, app_name="", pvt_corners=[], conditional_flow=""):
        try:
            job_id = str(uuid.uuid4())
            # 분류 체계 데이터 생성
            scheme_data = []
            for scheme in self.classification_schemes:
                scheme_data.append({"value": scheme["key"], "label": scheme["name"]})

            pvt_section_style = {"display": "none"}
            if app_name:
                if self.app_configs[app_name].get("pvt_inputs", False):
                    pvt_section_style = {"display": "block"}

            conditional_input_flow_style = {"display": "none"}
            conditional_input_flow_datas = []
            if app_name:
                if self.app_configs[app_name].get("conditional_input_flow", False):
                    conditional_input_flow_style = {"display": "block"}
                    conditional_input_flow_datas = self.app_configs[app_name]["conditional_input_flow"][0].get("flows", [])

            card = dmc.Card(
                [
                    dmc.CardSection(
                        [
                            dmc.Text("Signoff Application", fw=700, size="lg", mb=10),
                            # 분류 체계 선택 (Design Phase, Tool Category)
                            dmc.Text("Select Classification Scheme", size="sm", c="dimmed", mb=5),
                            dmc.SegmentedControl(
                                id={"type": "classification-scheme-segmented", "index": job_id},
                                data=scheme_data if scheme_data else [{"value": "none", "label": "No classifications available"}],
                                fullWidth=True,
                                color="indigo",
                                value="none",
                            ),
                            dmc.Space(h=10),
                            # 애플리케이션 선택 (카테고리가 그룹으로 표시됨)
                            dmc.Select(
                                id={"type": "signoff-app-select", "index": job_id},
                                data=[app_name],
                                value=app_name,
                                label="Select Signoff Application",
                                placeholder="Select an application...",
                                searchable=True,
                                clearable=True,
                                styles={"groupLabel": {"fontSize": "1.2rem", "fontWeight": "bold"}},
                            ),
                        ],
                        inheritPadding=True,
                        py="xs",
                    ),
                    dmc.Divider(),
                    self._create_pvt_section(job_id, pvt_corners, pvt_section_style),
                    dmc.Divider(),
                    self._create_conditional_input_flow(job_id, conditional_input_flow_datas, conditional_input_flow_style, conditional_flow),
                    dmc.Divider(),
                    dmc.CardSection(
                        [
                            dmc.Group(
                                [
                                    dbpc.Button(
                                        "Send Tool Manual",
                                        id={"type": "send-tool-manual-btn", "index": job_id},
                                        n_clicks=0,
                                        intent="success",
                                        icon="document-open",
                                        outlined=True,
                                        small=True,
                                    ),
                                    dbpc.Button(
                                        "Delete Job", id={"type": "delete-job-card-btn", "index": job_id}, n_clicks=0, intent="danger", icon="trash", outlined=True, small=True
                                    ),
                                ],
                                gap="sm",
                                justify="flex-end",
                            )
                        ],
                        inheritPadding=True,
                        py="xs",
                    ),
                ],
                withBorder=True,
                shadow="md",
                radius="sm",
                style={"overflow": "visible"},
                p="lg",
                id={"type": "job-card", "index": job_id},
            )
            return card

        except Exception as e:
            self.logger.error(f"Error:{e}")
            raise

    def create_pvt_condition_row(self, job_id, row_id, process="SSP", voltage="HV", temperature="CT"):
        return dmc.Group(
            [
                dmc.Select(
                    label="PROCESS",
                    data=["SSP", "TT", "SS", "FF"],
                    id={"type": "select-process", "index": job_id, "row": row_id},
                    value=process,
                    searchable=True,
                    nothingFoundMessage="Not supported option...",
                    size="xs",
                    style={"width": "30%"},
                ),
                dmc.Select(
                    label="VOLTAGE",
                    data=["HV", "LV"],
                    id={"type": "select-voltage", "index": job_id, "row": row_id},
                    value=voltage,
                    searchable=True,
                    nothingFoundMessage="Not supported option...",
                    size="xs",
                    style={"width": "30%"},
                ),
                dmc.Select(
                    label="TEMPERATURE",
                    data=["HT", "CT"],
                    id={"type": "select-temperature", "index": job_id, "row": row_id},
                    value=temperature,
                    searchable=True,
                    nothingFoundMessage="Not supported option...",
                    size="xs",
                    style={"width": "30%"},
                ),
            ],
            id={"type": "pvt-row", "index": job_id, "row": row_id},
            grow=True,
            align="flex-end",
        )

    def _merge_with_defaults(self, app_name, provided_inputs):
        try:
            """제공된 입력값과 기본값을 병합"""
            default_inputs = self._get_default_inputs(app_name)
            merged_inputs = default_inputs.copy()
            merged_inputs.update(provided_inputs)  # 제공된 값으로 덮어씁니다
            return merged_inputs
        except Exception as e:
            self.logger.error(f"Error: {e}")
            raise

    def _create_pvt_section(self, job_id, pvt_corners, pvt_section_style):
        """PVT 섹션 생성"""
        pvt_rows = []
        if pvt_corners:
            for i, corner in enumerate(pvt_corners):
                pvt_rows.append(
                    self.create_pvt_condition_row(
                        job_id,
                        i,
                        process=corner.get("PROCESS", "TT"),
                        voltage=corner.get("VOLTAGE", "HV"),
                        temperature=corner.get("TEMPERATURE", "CT"),
                    )
                )
        else:
            pvt_rows = [self.create_pvt_condition_row(job_id, 0)]
        return dmc.CardSection(
            [
                dmc.Group(
                    [
                        dmc.Text("PVT Conditions", fw=700, size="lg", mb=10),
                        dbpc.Button(
                            minimal=True,
                            outlined=True,
                            id={"type": "add-pvt-btn", "index": job_id},
                            icon="plus",
                            small=True,
                        ),
                        dbpc.Button(
                            minimal=True,
                            outlined=True,
                            id={"type": "delete-pvt-row", "index": job_id},
                            icon="minus",
                            small=True,
                        ),
                    ]
                ),
                html.Div(pvt_rows, id={"type": "pvt-container", "index": job_id}),
            ],
            id={"type": "pvt-section", "index": job_id},
            inheritPadding=True,
            py="xs",
            style=pvt_section_style,
        )

    def _create_conditional_input_flow(self, job_id, flow_datas, conditional_input_flow_style, conditional_flow):
        conditional_checkbox_inputs = []
        for data in flow_datas:
            print(f"_create_conditional_input_flow: {data}")
            if data == conditional_flow:
                conditional_checkbox_inputs.append(dmc.Checkbox(label=data, value=data, checked=True, id={"type": "checkbox-flow", "index": job_id, "flow": data}))
            else:
                conditional_checkbox_inputs.append(dmc.Checkbox(label=data, value=data, id={"type": "checkbox-flow", "index": job_id, "flow": data}))
        return dmc.CardSection(
            children=[
                dmc.Group(
                    id={"type": "checkgroup-flow", "index": job_id},
                    style={"display": "flex", "flexDirection": "column", "alignItems": "flex-start"},
                    children=conditional_checkbox_inputs,
                )
            ],
            id={"type": "conditional-input-flow", "index": job_id},
            inheritPadding=True,
            py="xs",
            style=conditional_input_flow_style,
        )

    def _get_default_inputs(self, app_name):
        """앱의 필수 입력값들의 기본값을 가져옴"""
        default_inputs = {}

        app_config = self.app_configs.get(app_name, {})

        for input_config in app_config.get("inputs", []):
            input_name = input_config["name"]
            if input_config.get("required", True):
                default_inputs[input_name] = input_config.get("default", "")

        return default_inputs

    def _get_apps_data_by_scheme(self, scheme_key):
        """선택된 분류 체계에 따라 애플리케이션 데이터 생성"""
        app_data = []

        # 분류 체계가 없거나 유효하지 않은 경우
        if not self.classification_schemes or scheme_key == "none":
            # 전체 애플리케이션을 하나의 그룹에 표시
            all_apps = []
            for app_name in self.app_configs:
                all_apps.append({"value": app_name, "label": app_name})

            if all_apps:
                app_data.append({"group": "All Applications", "items": all_apps})
            return app_data

        # 선택된 분류 체계 찾기
        selected_scheme = None
        for scheme in self.classification_schemes:
            if scheme["key"] == scheme_key:
                selected_scheme = scheme
                break

        if not selected_scheme:
            return app_data

        # 카테고리별로 애플리케이션 그룹화
        for category in selected_scheme.get("categories", []):
            category_name = category["name"]
            category_desc = category.get("description", "")

            # 그룹 레이블 생성
            group_label = category_name
            if category_desc:
                group_label += f" ({category_desc})"

            # 카테고리에 해당하는 앱 목록 수집
            category_apps = []
            for app_name in category.get("applications", []):
                # 고유 식별자 생성 (카테고리_앱이름 형식)
                unique_id = f"{category_name}_{app_name}"

                # 실제로 존재하는 앱만 포함
                if app_name in self.app_configs:
                    category_apps.append({"value": unique_id, "label": app_name, "app_name": app_name})  # 고유 식별자  # 표시용 이름  # 실제 앱 이름 (추후 처리용)

            # 빈 카테고리는 제외
            if category_apps:
                app_data.append({"group": group_label, "items": category_apps})

        return app_data

    def layout(self):
        return dmc.Stack(
            [
                dmc.Group(
                    [
                        dbpc.Button(
                            "Create Job",
                            id="create-job-card-btn",
                            icon="plus",
                        ),
                        dmc.Indicator(
                            dbpc.Button(
                                "Add Jobs",
                                id="add-jobs-btn",
                                fill=True,
                                icon="play",
                                intent="success",
                                disabled=True,
                            ),
                            id="job-count-indicator",
                            inline=True,
                            color="green",
                            disabled=True,
                            size=16,
                            label="",
                            position="top-end",
                        ),
                    ],
                    grow=True,
                ),
                dmc.Stack(
                    children=[],
                    id="creating-jobs-container",
                    gap="sm",
                ),
                dcc.Store(id="edit-from-queue", data={}),
            ]
        )

    def _register_callbacks(self, app):
        @app.callback(
            Output("creating-jobs-container", "children", allow_duplicate=True),
            Input("create-job-card-btn", "n_clicks"),
            prevent_initial_call=True,
        )
        def add_new_job_card(n_clicks):
            try:
                if n_clicks is None:
                    return no_update
                patched_job_cards = Patch()
                patched_job_cards.append(self.create_job_card())
                return patched_job_cards
            except Exception as e:
                self.logger.error(f"Error adding new job card: {e}")
                raise exceptions.PreventUpdate

        @app.callback(
            Output("creating-jobs-container", "children", allow_duplicate=True),
            Output({"type": "delete-job-card-btn", "index": ALL}, "n_clicks"),
            Input({"type": "delete-job-card-btn", "index": ALL}, "n_clicks"),
            State("creating-jobs-container", "children"),
            prevent_initial_call=True,
        )
        def delete_job_card(n_clicks, current_jobs):
            try:
                if not ctx.triggered_id or sum(n_clicks) == 0:
                    raise exceptions.PreventUpdate

                deleted_index = ctx.triggered_id["index"]
                current_jobs = [job for job in current_jobs if job["props"]["id"]["index"] != deleted_index]
                ret_n_clicks = [0] * len(n_clicks)
                return current_jobs, ret_n_clicks
            except Exception as e:
                raise exceptions.PreventUpdate

        @app.callback(
            Output({"type": "signoff-app-select", "index": MATCH}, "data"),
            Output({"type": "signoff-app-select", "index": MATCH}, "value"),
            Input({"type": "classification-scheme-segmented", "index": MATCH}, "value"),
            prevent_initial_call=True,
        )
        def update_applications_by_scheme(scheme_key):
            print(f"분류 체계 선택에 따라 애플리케이션 목록 업데이트 scheme_key: {scheme_key}")
            """분류 체계 선택에 따라 애플리케이션 목록 업데이트"""
            if not scheme_key:
                return [], None

            # 분류 체계에 따라 애플리케이션 데이터 생성
            app_data = self._get_apps_data_by_scheme(scheme_key)
            print(f"app_data: {app_data}")
            return app_data, None

        @self.app.callback(
            Output({"type": "conditional-input-flow", "index": MATCH}, "style"),
            Output({"type": "checkgroup-flow", "index": MATCH}, "children"),
            Output({"type": "pvt-section", "index": MATCH}, "style"),
            Output({"type": "job-card", "index": MATCH}, "style"),
            Output({"type": "signoff-app-select", "index": MATCH}, "color"),
            Output({"type": "pvt-container", "index": MATCH}, "children", allow_duplicate=True),
            Input({"type": "signoff-app-select", "index": MATCH}, "value"),
            State({"type": "pvt-container", "index": MATCH}, "children"),
            State({"type": "checkgroup-flow", "index": MATCH}, "id"),
            prevent_initial_call=True,
        )
        def update_job_card_color(selected_value, existing_corners, checkgroup_id):
            if not selected_value:
                raise exceptions.PreventUpdate

            # 고유 식별자에서 실제 앱 이름 추출
            if IDENTIFIER in selected_value:
                # 카테고리_앱이름 형식에서 앱 이름 추출
                app_name = selected_value.split(IDENTIFIER, 1)[1]
            else:
                # 기존 형식 (고유 식별자가 아닌 경우)
                app_name = selected_value

            if app_name not in self.app_configs:
                logger.warning(f"App {app_name} not found in app_configs")
                raise exceptions.PreventUpdate

            if self.app_configs[app_name].get("pvt_inputs", False):
                pvt_style = {"display": "block"}
            else:
                pvt_style = {"display": "none"}
                existing_corners = [existing_corners[0]]

            if self.app_configs[app_name].get("conditional_input_flow", False):
                conditional_input_flow_style = {"display": "block"}
                conditional_input_flow_datas = self.app_configs[app_name]["conditional_input_flow"][0].get("flows")
            else:
                conditional_input_flow_style = {"display": "none"}
                conditional_input_flow_datas = []

            conditional_checkbox_inputs = []
            for data in conditional_input_flow_datas:
                conditional_checkbox_inputs.append(dmc.Checkbox(label=data, value=data, id={"type": "checkbox-flow", "index": checkgroup_id.get("index"), "flow": data}))

            selected_color = self.app_configs[app_name]["color"]
            card_style = {"overflow": "visible", "borderColor": selected_color}

            return conditional_input_flow_style, conditional_checkbox_inputs, pvt_style, card_style, selected_color, existing_corners

        @app.callback(
            Output({"type": "pvt-container", "index": MATCH}, "children"),
            Input({"type": "add-pvt-btn", "index": MATCH}, "n_clicks"),
            Input({"type": "delete-pvt-row", "index": MATCH}, "n_clicks"),
            State({"type": "pvt-container", "index": MATCH}, "children"),
            prevent_initial_call=True,
        )
        def manage_pvt_corner_splits(add_clicks, delete_clicks, existing_corners):
            """Callback to manage PVT corners in a job card"""
            ctx_msg = ctx.triggered[0]
            triggered_id = json.loads(ctx_msg["prop_id"].split(".")[0])
            job_id = triggered_id["index"]

            if triggered_id["type"] == "add-pvt-btn":
                if len(existing_corners) < self.MAX_PVT_CORNERS:  # Maximum 5 corners allowed
                    new_row_id = len(existing_corners)
                    existing_corners.append(self.create_pvt_condition_row(job_id, new_row_id))

            elif triggered_id["type"] == "delete-pvt-row":
                if len(existing_corners) > self.MIN_PVT_CORNERS:  # Keep at least one corner
                    existing_corners.pop()

            return existing_corners

        @self.app.callback(
            Output("creating-jobs-container", "children", allow_duplicate=True),
            Input("edit-from-queue", "data"),
            prevent_initial_call=True,
        )
        def edit_from_queue_table(data):
            try:
                if not data:
                    raise exceptions.PreventUpdate
                patched_job_cards = Patch()
                pvt_corners = [{"PROCESS": data.get("PROCESS", ""), "VOLTAGE": data.get("VOLTAGE", ""), "TEMPERATURE": data.get("TEMPERATURE", "")}]
                patched_job_cards.append(self.create_job_card(data.get("APPLICATION", ""), pvt_corners, data.get("CONDITIONAL_FLOW", "")))

                return patched_job_cards
            except Exception as e:
                self.logger.error(f"Error edit from queue table: {str(e)}")
                raise exceptions.PreventUpdate
```

## File: job_set/jobInputs.py
```python
import os
import dash_blueprint_components as dbpc
import dash_mantine_components as dmc
from utils.logger import logger
from utils.sol_constants import IDENTIFIER
from dash import Input, Output, State, dcc, html, ALL, ctx, no_update, exceptions, MATCH


class JobInputs:
    def __init__(self, app, app_config):
        self.app_config = app_config
        self.input_field_registry = {}
        self.pvt_input_field_registry = {}
        self._register_callbacks(app)
        self.active_apps = []

    def update_app_config(self):
        self.app_config = app_config

    def layout(self):
        return dbpc.Card(
            children=[
                dbpc.EntityTitle(title="Application Inputs", heading="H3"),
                dmc.Space(h=20),
                dmc.SimpleGrid(id="file_inputs", cols=1, children=[], verticalSpacing="xs"),
                dmc.SimpleGrid(id="fileselect_inputs", cols=1, children=[], verticalSpacing="xs"),
                dmc.SimpleGrid(cols=4, children=[], id="number_inputs", verticalSpacing="xs"),
                dmc.SimpleGrid(cols=4, children=[], id="text_inputs", verticalSpacing="xs"),
                dmc.SimpleGrid(cols=1, children=[], id="textarea_inputs", verticalSpacing="xs"),
                dmc.SimpleGrid(cols=4, children=[], id="select_inputs", verticalSpacing="xs"),
                dmc.SimpleGrid(cols=4, children=[], id="multiselect_inputs", verticalSpacing="xs"),
                dmc.SimpleGrid(cols=4, children=[], id="checkbox_inputs", verticalSpacing="xs"),
                dmc.Space(h=10),
                # PVT 의존성 입력을 위한 새로운 섹션
                dmc.Stack(
                    [
                        # dbpc.EntityTitle(title="PVT-Dependent Inputs", heading="H4"),
                        dmc.SimpleGrid(
                            id="pvt-dependent-inputs",
                            cols=1,
                            children=[],
                            verticalSpacing="xs",
                        ),
                        dmc.Space(h=10),
                    ]
                ),
                dcc.Store(id="baap-store"),
                html.Div(id="optional-inputs"),
                html.Div(id="conditional-inputs"),
            ],
            elevation=2,
        )

    def _get_input_field(self, input_config, app_name, preset_value=None, flow=""):
        """
        입력 필드 생성 또는 기존 필드 업데이트
        """
        field_id = input_config["name"].replace("_", "-")
        field_type = input_config["type"]

        # 이미 생성된 필드인 경우 앱 정보만 추가
        if field_id in self.input_field_registry and flow == self.input_field_registry[field_id]["flow"]:
            if app_name not in self.input_field_registry[field_id]["apps"]:
                self.input_field_registry[field_id]["apps"].append(app_name)
                self.input_field_registry[field_id]["field"].labelInfo.append(
                    dmc.Badge(
                        app_name,
                        size="xs",
                        variant="light",
                        radius="xs",
                        color=self.app_config[app_name]["color"],
                    )
                )

                # preset 값이 있는 경우 필드 값 업데이트
                if preset_value is not None:
                    if field_type == "file_input":
                        self.input_field_registry[field_id]["field"].children[0].text = preset_value
                    elif field_type == "number_input":
                        self.input_field_registry[field_id]["field"].children[0].value = str(preset_value)
                    elif field_type == "text_input":
                        self.input_field_registry[field_id]["field"].children[0].value = preset_value

            return self.input_field_registry[field_id]["field"]

        # 필드 설명 툴팁
        tooltip = input_config.get("description", "")

        # 값 설정 (preset 값이 있으면 사용, 없으면 default 값 사용)
        value = preset_value if preset_value is not None else input_config.get("default", "")

        # placeholder 값 설정 (placeholder 값이 있으면 사용, 없으면 "" 값 사용)
        placeholder = input_config.get("placeholder", "")

        if field_type == "file_input":
            field = self._file_input_field(
                input_config["name"], value, [app_name], tooltip, placeholder, input_config.get("required", True), input_config.get("error_check", True), flow
            )
        elif field_type == "fileselect_input":
            field = self._fileselect_input_field(input_config["name"], value, input_config["datas"], [app_name], tooltip, placeholder, flow)
        elif field_type == "number_input":
            field = self._number_input_field(input_config["name"], value, [app_name], tooltip, input_config.get("unit", ""), placeholder, flow)
        elif field_type == "text_input":
            field = self._text_input_field(input_config["name"], value, [app_name], tooltip, placeholder, flow)
        elif field_type == "textarea_input":
            field = self._textarea_input_field(input_config["name"], value, [app_name], tooltip, placeholder, flow)
        elif field_type == "select_input":
            field = self._select_input_field(input_config["name"], value, [app_name], tooltip, input_config["datas"], placeholder, flow)
        elif field_type == "multiselect_input":
            field = self._multiselect_input_field(input_config["name"], value, [app_name], tooltip, input_config["datas"], placeholder, flow)
        elif field_type == "checkbox_input":
            field = self._checkbox_input_field(input_config["name"], value, [app_name], tooltip, flow)
        else:
            logger.error(f"Unsupported input type: {field_type}")
        self.input_field_registry[field_id] = {
            "field": field,
            "apps": [app_name],
            "type": field_type,
            "required": input_config.get("required", True),
            "flow": flow,
        }
        return field

    def _number_input_field(self, name, value, app_names, tooltip, unit="", placeholder="", flow=""):
        return dbpc.FormGroup(
            children=[
                dbpc.Tooltip(
                    content=tooltip,
                    hoverOpenDelay=3000,
                    compact=True,
                    minimal=True,
                    children=dmc.NumberInput(
                        id={"type": "number-input", "index": name.replace("_", "-"), "flow": flow}, value=str(value), size="xs", suffix=unit, placeholder=placeholder
                    ),
                )
            ],
            id={"type": "number-input-label", "index": name.replace("_", "-")},
            label=name.replace("_", " "),
            labelInfo=[
                dmc.Badge(
                    app_name,
                    size="xs",
                    variant="light",
                    radius="xs",
                    color=self.app_config[app_name]["color"],
                )
                for app_name in app_names
            ],
        )

    def _select_input_field(self, name, value, app_names, tooltip, datas, placeholder="", flow=""):
        return dbpc.FormGroup(
            children=[
                dbpc.Tooltip(
                    content=tooltip,
                    hoverOpenDelay=3000,
                    compact=True,
                    minimal=True,
                    children=dmc.Select(
                        id={"type": "select-input", "index": name.replace("_", "-"), "flow": flow},
                        value=str(value),
                        data=datas,
                        placeholder=placeholder,
                        size="xs",
                    ),
                )
            ],
            id={"type": "select-input-label", "index": name.replace("_", "-")},
            label=name.replace("_", " "),
            labelInfo=[dmc.Badge(app_name, size="xs", variant="light", radius="xs", color=self.app_config[app_name]["color"]) for app_name in app_names],
        )

    def _text_input_field(self, name, value, app_names, tooltip, placeholder="", flow=""):
        return dbpc.FormGroup(
            children=[
                dbpc.Tooltip(
                    content=tooltip,
                    hoverOpenDelay=3000,
                    compact=True,
                    minimal=True,
                    children=dbpc.InputGroup(id={"type": "text-input", "index": name.replace("_", "-"), "flow": flow}, value=value, placeholder=placeholder),
                )
            ],
            id={"type": "text-input-label", "index": name.replace("_", "-")},
            label=name.replace("_", " "),
            labelInfo=[
                dmc.Badge(
                    app_name,
                    size="xs",
                    variant="light",
                    radius="xs",
                    color=self.app_config[app_name]["color"],
                )
                for app_name in app_names
            ],
        )

    def _textarea_input_field(self, name, value, app_names, tooltip, placeholder="", flow=""):
        return dbpc.FormGroup(
            children=[
                dbpc.Tooltip(
                    content=tooltip,
                    hoverOpenDelay=3000,
                    compact=True,
                    minimal=True,
                    fill=True,
                    children=dmc.Textarea(
                        id={"type": "textarea-input", "index": name.replace("_", "-"), "flow": flow}, value=value, placeholder=placeholder, autosize=True, minRows=1
                    ),
                )
            ],
            id={"type": "textarea-input-label", "index": name.replace("_", "-")},
            label=name.replace("_", " "),
            labelInfo=[
                dmc.Badge(
                    app_name,
                    size="xs",
                    variant="light",
                    radius="xs",
                    color=self.app_config[app_name]["color"],
                )
                for app_name in app_names
            ],
        )

    def _file_input_field(self, name, value, app_names, tooltip, placeholder="", required=True, error_check=True, flow=""):
        return dbpc.FormGroup(
            children=[
                dbpc.Tooltip(
                    content=tooltip,
                    hoverOpenDelay=3000,
                    compact=True,
                    minimal=True,
                    fill=True,
                    children=dmc.TextInput(
                        value=value,
                        placeholder=placeholder,
                        leftSection=dmc.ActionIcon(
                            dbpc.Icon(icon="search", size=12),
                            id={"type": "file-search-btn", "index": name.replace("_", "-"), "flow": flow},
                            variant="subtle",
                            n_clicks=0,
                            color="black",
                        ),
                        rightSection=dbpc.Button(
                            "Gvim",
                            icon="edit",
                            id={"type": "file-gvim-btn", "index": name.replace("_", "-"), "flow": flow},
                            disabled=True,
                        ),
                        rightSectionWidth=80,
                        required=True,
                        id={"type": "file-input", "index": name.replace("_", "-"), "flow": flow},
                    ),
                ),
                dcc.Store(id={"type": "file-input-error-check", "index": name.replace("_", "-"), "flow": flow}, data=error_check),
            ],
            id={"type": "file-input-label", "index": name.replace("_", "-")},
            label=name.replace("_", " "),
            labelInfo=[
                dmc.Badge(
                    app_name,
                    size="xs",
                    variant="light",
                    radius="xs",
                    color=self.app_config[app_name]["color"],
                )
                for app_name in app_names
            ],
        )

    def _multiselect_input_field(self, name, value, app_names, tooltip, datas, placeholder="", flow=""):
        return dbpc.FormGroup(
            children=[
                dbpc.Tooltip(
                    content=tooltip,
                    hoverOpenDelay=3000,
                    compact=True,
                    minimal=True,
                    children=dmc.MultiSelect(
                        id={"type": "multiselect-input", "index": name.replace("_", "-"), "flow": flow},
                        data=datas,
                        placeholder=placeholder,
                        w=400,
                        clearable=True,
                        searchable=True,
                        hidePickedOptions=True,
                        limit=10,
                    ),
                )
            ],
            id={"type": "multiselect-input-label", "index": name.replace("_", "-")},
            label=name.replace("_", " "),
            labelInfo=[dmc.Badge(app_name, size="xs", variant="light", radius="xs", color=self.app_config[app_name]["color"]) for app_name in app_names],
        )

    def _fileselect_input_field(self, name, value, datas, app_names, tooltip, placeholder="", flow=""):
        return dbpc.FormGroup(
            children=[
                dbpc.Tooltip(
                    content=tooltip,
                    hoverOpenDelay=3000,
                    compact=True,
                    minimal=True,
                    fill=True,
                    children=dmc.Select(
                        value=value,
                        data=datas,
                        placeholder=placeholder,
                        rightSection=dbpc.Button(
                            "Gvim",
                            icon="edit",
                            id={"type": "file-select-gvim-btn", "index": name.replace("_", "-"), "flow": flow},
                            disabled=True,
                        ),
                        rightSectionWidth=80,
                        rightSectionPointerEvents="all",
                        required=True,
                        id={"type": "file-select-input", "index": name.replace("_", "-"), "flow": flow},
                    ),
                )
            ],
            id={"type": "file-input-select-label", "index": name.replace("_", "-")},
            label=name.replace("_", " "),
            labelInfo=[dmc.Badge(app_name, size="xs", variant="light", radius="xs", color=self.app_config[app_name]["color"]) for app_name in app_names],
        )

    def _checkbox_input_field(self, name, value, app_names, tooltip, flow=""):
        return dbpc.FormGroup(
            children=[
                dbpc.Tooltip(
                    content=tooltip,
                    hoverOpenDelay=3000,
                    compact=True,
                    minimal=True,
                ),
                dmc.Checkbox(
                    id={"type": "checkbox-input", "index": name.replace("_", "-"), "flow": flow},
                    checked=value,
                    label=name.replace("_", " "),
                ),
            ],
            id={"type": "checkbox-input-label", "index": name.replace("_", "-")},
            labelInfo=[dmc.Badge(app_name, size="xs", variant="light", radius="xs", color=self.app_config[app_name]["color"]) for app_name in app_names],
        )

    def _is_possible_file_path(self, file_path, required=True):
        if not file_path:
            if not required:
                return True
            return False
        if not os.path.isfile(file_path) or not os.path.isabs(file_path):
            logger.warning(f"Invalid file path: {file_path}")
            return False
        return True

    def _register_callbacks(self, app):
        @app.callback(
            Output("file_inputs", "children"),
            Output("fileselect_inputs", "children"),
            Output("number_inputs", "children"),
            Output("text_inputs", "children"),
            Output("textarea_inputs", "children"),
            Output("select_inputs", "children"),
            Output("multiselect_inputs", "children"),
            Output("checkbox_inputs", "children"),
            Output("optional-inputs", "children"),
            Output("conditional-inputs", "children", allow_duplicate=True),
            Output("baap-store", "data"),
            Input({"type": "signoff-app-select", "index": ALL}, "value"),
            State("edit-from-queue", "data"),
            prevent_initial_call=True,
        )
        def update_input_fields(signoff_values, queue_data):
            # 값이 None인 항목 제외하고 실제 앱 이름으로 변환
            active_apps = []
            for val in signoff_values:
                if val is None:
                    continue

                # 고유 식별자에서 실제 앱 이름 추출
                if "_" in val:
                    # 카테고리_앱이름 형식에서 앱 이름 추출
                    app_name = val.split(IDENTIFIER, 1)[1]
                else:
                    # 기존 형식 (고유 식별자가 아닌 경우)
                    app_name = val

                if app_name in self.app_config:
                    active_apps.append(app_name)

            if not active_apps:
                return [], [], [], [], [], [], [], [], [], [], False

            self.active_apps = active_apps

            self.input_field_registry = {}
            file_inputs = []
            fileselect_inputs = []
            number_inputs = []
            text_inputs = []
            textarea_inputs = []
            select_inputs = []
            multiselect_inputs = []
            checkbox_inputs = []
            optional_file_inputs = []
            optional_fileselect_inputs = []
            optional_number_inputs = []
            optional_text_inputs = []
            optional_textarea_inputs = []
            optional_select_inputs = []
            optional_multiselect_inputs = []
            optional_checkbox_inputs = []
            for app_name in active_apps:
                app_config = self.app_config[app_name]
                for input_config in app_config["inputs"]:
                    preset_value = input_config.get("default")
                    if queue_data.get("APPLICATION") == app_name:
                        preset_value = queue_data.get(input_config["name"], "")
                        preset_value = "" if preset_value is None else preset_value
                    field = self._get_input_field(input_config, app_name, preset_value)

                    # Determine if the field is required
                    is_required = input_config.get("required", True)

                    if input_config["type"] == "file_input":
                        target_list = file_inputs if is_required else optional_file_inputs
                        if field not in target_list:
                            target_list.append(field)
                    elif input_config["type"] == "fileselect_input":
                        target_list = fileselect_inputs if is_required else optional_fileselect_inputs
                        if field not in target_list:
                            target_list.append(field)
                    elif input_config["type"] == "number_input":
                        target_list = number_inputs if is_required else optional_number_inputs
                        if field not in target_list:
                            target_list.append(field)
                    elif input_config["type"] == "select_input":
                        target_list = select_inputs if is_required else optional_select_inputs
                        if field not in target_list:
                            target_list.append(field)
                    elif input_config["type"] == "multiselect_input":
                        target_list = multiselect_inputs if is_required else optional_multiselect_inputs
                        if field not in target_list:
                            target_list.append(field)
                    elif input_config["type"] == "text_input":
                        target_list = text_inputs if is_required else optional_text_inputs
                        if field not in target_list:
                            target_list.append(field)
                    elif input_config["type"] == "textarea_input":
                        target_list = textarea_inputs if is_required else optional_textarea_inputs
                        if field not in target_list:
                            target_list.append(field)
                    elif input_config["type"] == "checkbox_input":
                        target_list = checkbox_inputs if is_required else optional_checkbox_inputs
                        if field not in target_list:
                            target_list.append(field)

            if (
                optional_file_inputs
                + optional_fileselect_inputs
                + optional_number_inputs
                + optional_select_inputs
                + optional_text_inputs
                + optional_textarea_inputs
                + optional_multiselect_inputs
                + optional_checkbox_inputs
            ):
                optional_inputs = dmc.Stack(
                    children=[
                        dmc.Divider(variant="solid"),
                        dbpc.Button(
                            id="optional-collapse-btn",
                            icon="key-option",
                            children="Optional Inputs",
                            outlined=True,
                        ),
                        dmc.Space(h=10),
                        dbpc.Collapse(
                            id="optional-input-collapse",
                            isOpen=False,
                            children=[
                                dmc.SimpleGrid(optional_file_inputs, cols=1, verticalSpacing="xs", id="optional-file-inputs"),
                                dmc.SimpleGrid(optional_fileselect_inputs, cols=1, verticalSpacing="xs", id="optional-fileselect-inputs"),
                                dmc.SimpleGrid(optional_textarea_inputs, cols=1, verticalSpacing="xs", id="optional-textarea-inputs"),
                                dmc.SimpleGrid(optional_number_inputs, cols=4, verticalSpacing="xs", id="optional-number-inputs"),
                                dmc.SimpleGrid(optional_select_inputs, cols=4, verticalSpacing="xs", id="optional-select-inputs"),
                                dmc.SimpleGrid(optional_text_inputs, cols=4, verticalSpacing="xs", id="optional-text-inputs"),
                                dmc.SimpleGrid(optional_multiselect_inputs, cols=4, verticalSpacing="xs", id="optional-multiselect-inputs"),
                                dmc.SimpleGrid(optional_checkbox_inputs, cols=4, verticalSpacing="xs", id="optional-checkbox-inputs"),
                            ],
                        ),
                    ]
                )
            else:
                optional_inputs = None

            return (
                file_inputs,
                fileselect_inputs,
                number_inputs,
                text_inputs,
                textarea_inputs,
                select_inputs,
                multiselect_inputs,
                checkbox_inputs,
                optional_inputs,
                [],
                True,
            )

        @app.callback(
            Output("pvt-dependent-inputs", "children"),
            Input({"type": "select-process", "index": ALL, "row": ALL}, "value"),
            Input({"type": "select-voltage", "index": ALL, "row": ALL}, "value"),
            Input({"type": "select-temperature", "index": ALL, "row": ALL}, "value"),
            State({"type": "signoff-app-select", "index": ALL}, "value"),
            State({"type": "signoff-app-select", "index": ALL}, "id"),
            State({"type": "select-process", "index": ALL, "row": ALL}, "id"),
            State("edit-from-queue", "data"),
            prevent_initial_call=True,
        )
        def update_pvt_dependent_inputs(
            process_vals,
            voltage_vals,
            temp_vals,
            signoff_values,
            signoff_tools_ids,
            process_ids,
            queue_data,
        ):
            """PVT 설정에 따라 필요한 입력 필드만 표시"""
            if not signoff_values:
                return []

            ctx_triggered = ctx
            if not ctx_triggered:
                return no_update

            # 현재 PVT 설정 추출
            current_pvt = {
                "PROCESS": process_vals,
                "VOLTAGE": voltage_vals,
                "TEMPERATURE": temp_vals,
            }

            visible_fields = []
            self.input_field_registry = {}

            pvt_index = [d["index"] for d in process_ids]
            tool_index_map = {}

            # signoff_values에서 실제 앱 이름으로 변환하여 매핑
            for i, d in enumerate(signoff_tools_ids):
                index = d["index"]
                value = signoff_values[i]

                if value is not None:
                    # 고유 식별자에서 실제 앱 이름 추출
                    if "_" in value:
                        app_name = value.split("_", 1)[1]
                    else:
                        app_name = value

                    tool_index_map[index] = app_name

            try:
                for i, index in enumerate(pvt_index):
                    app_name = tool_index_map[index]
                    if app_name:
                        app_config = self.app_config[app_name]

                        for input_config in app_config.get("pvt_inputs", []):
                            depends_on = input_config.get("depends_on", {})
                            for pvt_type, required_values in depends_on.items():
                                if current_pvt[pvt_type][i] == required_values:
                                    field = self._get_input_field(input_config, app_name, queue_data.get(input_config.get("name", "")))
                                    if field not in visible_fields:
                                        visible_fields.append(field)

                if visible_fields:
                    return [dbpc.EntityTitle(title="PVT-Dependent Inputs", heading="H6")] + visible_fields
                else:
                    return visible_fields

            except Exception as e:
                print(f"Error: {e}")

        @app.callback(
            Output({"type": "conditional-inputs-collapse", "index": MATCH}, "isOpen"),
            Input({"type": "conditional-inputs-collapse-btn", "index": MATCH}, "n_clicks"),
            State({"type": "conditional-inputs-collapse", "index": MATCH}, "isOpen"),
            prevent_initial_call=True,
        )
        def collapse_conditional_inputs(_, isOpen):
            return False if isOpen else True

        @app.callback(
            Output("optional-input-collapse", "isOpen"),
            Input("optional-collapse-btn", "n_clicks"),
            State("optional-input-collapse", "isOpen"),
            prevent_initial_call=True,
        )
        def collapse_optional_inputs(_, isOpen):
            return False if isOpen else True

        @app.callback(
            Output("conditional-inputs", "children"),
            Input({"type": "checkbox-flow", "index": ALL, "flow": ALL}, "checked"),
            State({"type": "checkbox-flow", "index": ALL, "flow": ALL}, "value"),
            State("edit-from-queue", "data"),
            prevent_initial_call=True,
        )
        def update_conditional_input_fields(conditional_checked, conditional_value, queue_data):
            if all(not item for item in conditional_checked) or not self.active_apps:
                return []
            conditional_flow_set = set(item2 for item1, item2 in zip(conditional_checked, conditional_value) if item1)
            conditional_inputs = []
            for flow in conditional_flow_set:
                fields = []
                for app_name in self.active_apps:
                    app_config = self.app_config[app_name].get("conditional_input_flow")
                    if app_config:
                        for config in app_config:
                            if flow in config.get("flow_names", []):
                                preset_value = config.get("default")
                                if queue_data.get(config.get("name", "")):
                                    preset_value = queue_data.get(config.get("name", ""))
                                    preset_value = "" if preset_value is None else preset_value
                                field = self._get_input_field(config, app_name, preset_value, flow)
                                if field not in fields:
                                    fields.append(field)

                conditional_flow_layout = dmc.Stack(
                    children=[
                        dmc.Divider(variant="solid"),
                        dbpc.Button(
                            id={"type": "conditional-inputs-collapse-btn", "index": f"{flow}"},
                            icon="key-option",
                            children=f"{flow} Inputs",
                            outlined=True,
                        ),
                        dmc.Space(h=10),
                        dbpc.Collapse(
                            id={"type": "conditional-inputs-collapse", "index": f"{flow}"},
                            isOpen=False,
                            children=[dmc.SimpleGrid(fields, cols=1, verticalSpacing="xs", id=f"{flow}-inputs")],
                        ),
                    ]
                )
                conditional_inputs.append(conditional_flow_layout)

            return conditional_inputs
```

## File: job_set/jobManager.py
```python
import os
import yaml
import shutil
import subprocess
from datetime import datetime
from utils.logger import logger
from utils.workspace import get_workspace_dir
from utils.settings import RUN_SCRIPTS, SIGNOFF_APPLICATION_YAML
from utils.config_loader import ConfigLoader


class JobManager:
    """Manager for SignOff job creation and execution"""

    def __init__(self, app_name, subckt, job_name, conditional_flow, corner, inputs):
        """Initialize JobManager for specific job"""

        self.app_name = app_name
        self.subckt = subckt
        self.corner = corner
        self.custom_jobname = job_name
        self.inputs = inputs
        self.conditional_flow = conditional_flow

        # Job specific attributes
        self.job_name = None
        self.job_dir = None
        self.job_config = None
        self.pid = None
        self.app_run_dir = None
        self.env_file = None
        self.mlm_link = None

        # Initialize logger
        self.logger = logger.getChild(f"job.{app_name}")

    def _generate_job_name(self):
        """Generate unique job directory name"""
        name = self.app_name
        if self.custom_jobname:
            name += f"_{self.custom_jobname}"
        if self.corner:
            name += f"_{self.corner['process']}{self.corner['voltage']}{self.corner['temperature']}"
        if self.subckt:
            name += f"_{self.subckt}"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.job_name = f"{name}_{timestamp}"
        return self.job_name

    def _get_runscript_path(self, app_name, yaml_file):
        with open(yaml_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            for app in data.get("applications", []):
                if app.get("name") == app_name:
                    return app.get("runscript_path")
        return None

    def _create_directories(self):
        """Create job directory structure"""
        base_job_dir = os.path.join(get_workspace_dir(), self.job_name)
        self.job_dir = base_job_dir
        counter = 1

        while os.path.exists(self.job_dir):
            self.job_dir = f"{base_job_dir}_{counter}"
            self.job_name = f"{self.job_name}_{counter}"
            counter += 1

        os.makedirs(self.job_dir, exist_ok=True)

        # Copy RunScripts
        app_scripts_dir = self._get_runscript_path(self.app_name, SIGNOFF_APPLICATION_YAML)

        if os.path.exists(app_scripts_dir):
            self.app_run_dir = os.path.join(self.job_dir, self.app_name)
            shutil.copytree(app_scripts_dir, self.app_run_dir)
            for subdir in ["LOG", "SETUP", "RESULT"]:
                os.makedirs(os.path.join(self.app_run_dir, subdir), exist_ok=True)

    def _create_job_config(self):
        """Create job configuration file"""
        self.job_config = {
            "name": self.job_name,
            "app": self.app_name,
            "corners": self.corner,
            "inputs": self.inputs,
            "workspace": self.job_dir,
            "output_filename": "result",
            "status": "pending",
            "job_id": None,
            "pid": None,
            "message": None,
            "job_start_time": None,
            "job_finish_time": None,
            "owner": "",
            "mlm": self.mlm_link,
        }
        config_path = os.path.join(self.job_dir, "job_config.yaml")
        with open(config_path, "w") as f:
            yaml.dump(self.job_config, f, default_flow_style=False)

    def _create_env_file(self):
        """Create environment setup file"""
        self.env_file = os.path.join(self.job_dir, "env")
        config_loader = ConfigLoader()
        app_config = config_loader.app_configs

        with open(self.env_file, "w") as f:
            # Basic settings
            f.write(f"setenv PATH '/user/signoff.dsa/miniconda3/envs/launcher/bin:$PATH\n\n")
            f.write(f"setenv APP {self.app_name}\n\n")

            # Corner settings
            if self.corner:
                f.write("# Corner Settings\n")
                f.write(f"setenv PROCESS {self.corner['process']}\n")
                f.write(f"setenv VOLTAGE {self.corner['voltage']}\n")
                f.write(f"setenv TEMPERATURE {self.corner['temperature']}\n\n")

            # 애플리케이션별 설정
            f.write("# Input Settings\n")

            for setting in app_config[self.app_name]["inputs"]:
                env_name = setting["name"].upper()
                value = self.inputs.get(setting["name"], "")

                # 파일 경로나 문자열인 경우 따옴표로 감싸기
                if setting["type"] in ["file_input", "text_input", "textarea_input", "select_input", "multiselect_input"]:
                    f.write(f"setenv {env_name} '{value}'\n")
                else:
                    f.write(f"setenv {env_name} {value}\n")

            pvt_inputs = app_config[self.app_name].get("pvt_inputs", [])
            for setting in pvt_inputs:
                env_name = setting["name"].upper()
                value = self.inputs.get(setting["name"], "")
                # 파일 경로나 문자열인 경우 따옴표로 감싸기
                if setting["type"] in ["file_input", "text_input", "textarea_input", "select_input", "multiselect_input"]:
                    f.write(f"setenv {env_name} '{value}'\n")
                else:
                    f.write(f"setenv {env_name} {value}\n")

            # 출력 파일 이름 설정
            f.write(f"setenv OUTPUT_FILENAME 'result'\n")

    def _update_input_config(self):
        """run.sh 실행을 위해 RUNSCRIPT의 input_config.yaml 파일의 default 값들을 업데이트"""
        try:
            # RUNSCRIPT의 input_config.yaml 경로
            input_config_path = os.path.join(self.app_run_dir, "input_config.yaml")

            # 기존 input_config.yaml 읽기
            with open(input_config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            app_config = config[self.app_name]

            # MLM Link 업데이트
            if "mlm_link" in app_config:
                self.mlm_link = app_config["mlm_link"]

            # Regular inputs 업데이트
            if "inputs" in app_config:
                for input_item in app_config["inputs"]:
                    input_name = input_item["name"]
                    if input_name in self.inputs:
                        input_item["default"] = self.inputs[input_name]

            # Corner dependent inputs 업데이트
            if "pvt_inputs" in app_config and self.corner:
                for pvt_input in app_config["pvt_inputs"]:
                    input_name = pvt_input["name"]

                    if input_name == "PROCESS":
                        pvt_input["default"] = self.corner["PROCESS"]
                    elif input_name == "VOLTAGE":
                        pvt_input["default"] = self.corner["VOLTAGE"]
                    elif input_name == "TEMPERATURE":
                        pvt_input["default"] = self.corner["TEMPERATURE"]

                    # depends_on 조건 확인
                    elif "depends_on" in pvt_input:
                        depends_on = pvt_input["depends_on"]
                        should_update = all(self.corner.get(pvt_type) == required_value for pvt_type, required_value in depends_on.items())

                        # 조건이 맞는 경우만 업데이트
                        if should_update and input_name in self.inputs:
                            pvt_input["default"] = self.inputs[input_name]

            if "conditional_input_flow" in app_config:
                for flow_input in app_config["conditional_input_flow"]:
                    input_name = flow_input.get("name")
                    if not input_name:
                        flows = flow_input.get("flows")
                        if flows and self.conditional_flow in flows:
                            flow_input["flows"] = self.conditional_flow
                        continue
                    input_flow = flow_input["flow_names"]
                    if input_name in self.inputs and self.conditional_flow in input_flow:
                        flow_input["default"] = self.inputs[input_name]

            # 업데이트된 config 저장
            with open(input_config_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False)

            self.logger.info(f"Successfully updated input_config.yaml for {self.app_name}")

        except Exception as e:
            error_msg = f"Error updating input_config.yaml: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def setup(self):
        """Setup job directory and configuration"""
        try:
            self._generate_job_name()  # 작업 이름 생성
            self._create_directories()  # 작업 디렉토리 생성 및 RUN SCRIPT 복사
            self._update_input_config()
            self._create_job_config()  # job_config 생성
            # self._create_env_file()  # job env 생성

            self.logger.info(f"Job setup completed: {self.job_name}")
            return self.job_dir

        except Exception as e:
            self.logger.error(f"Error in job setup: {str(e)}")
            raise

    def run(self):
        """Run the job"""
        logger.debug("Run  job")
        try:
            if not self.job_dir:
                raise ValueError("Job not setup. Call setup() first")

            # Update job status
            self.job_config.update(
                {
                    "status": "pending",
                    "owner": os.getenv("USER"),
                    "job_start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            with open(os.path.join(self.job_dir, "job_config.yaml"), "w", encoding="utf-8") as f:
                yaml.dump(self.job_config, f, default_flow_style=False)

            log_path = os.path.join(self.app_run_dir, "LOG", "stdout.log")

            # 로그 파일 생성 및 디스크립터 얻기
            stdout_fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
            stderr_fd = os.dup(stdout_fd)  # stderr도 동일 파일에 쓰기

            try:
                cmd = f"launcher_sub -cmd {os.path.join(self.app_run_dir, 'run.sh')} -o {log_path}"
                process = subprocess.Popen(cmd, shell=True, executable="/bin/csh", cwd=self.app_run_dir, stdout=stdout_fd, stderr=stderr_fd, preexec_fn=os.setpgrp)
            finally:
                os.close(stdout_fd)
                os.close(stderr_fd)
            self.pid = process.pid
            self.logger.info(f"Job started: {self.job_name} (PID: {self.pid})")

            return self.pid

        except Exception as e:
            self.logger.error(f"Error running job: {str(e)}")
            if self.job_config:
                self.job_config.update({"status": "failed", "message": str(e), "job_finish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                with open(os.path.join(self.job_dir, "job_config.yaml"), "w", encoding="utf-8") as f:
                    yaml.dump(self.job_config, f, default_flow_style=False)
            raise
```

## File: job_set/jobQueue.py
```python
import json
import uuid
import base64
import csv
import io
import pandas as pd
import dash_blueprint_components as dbpc
from dash import html, dcc, Input, Output, State, ctx, callback, no_update, exceptions
import dash_mantine_components as dmc
import dash_ag_grid as dag
import os
from utils.settings import USER_DIR
from utils.logger import logger


class JobQueue:
    def __init__(self, app):
        self.queue_backup_file = os.path.join(USER_DIR, f"queue_table.json")
        self._register_callbacks(app)

    def parse_job_data(self, application, corner, job_inputs, conditional_flow="", conditional_inputs={}):
        """입력 문자열을 파싱하여 job 데이터 생성"""
        try:
            row_data = {
                "_id": str(uuid.uuid4()),
                "APPLICATION": application,
                "JOBNAME": "",
                "CONDITIONAL_FLOW": conditional_flow ** job_inputs,
            }
            if corner:
                row_data.update(
                    {
                        "PROCESS": corner.get("PROCESS", ""),
                        "VOLTAGE": corner.get("VOLTAGE", ""),
                        "TEMPERATURE": corner.get("TEMPERATURE", ""),
                    }
                )
            return row_data

        except Exception as e:
            print(f"Error parsing job data: {e}")
            return None

    def save_queue_data(self, data):
        """Queue 테이블 데이터를 파일에 저장"""
        try:
            with open(self.queue_backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
            logger.info(f"Queue data saved to {self.queue_backup_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving queue data: {str(e)}")
            return False

    def load_queue_data(self):
        """저장된 Queue 테이블 데이터 로드"""
        try:
            if os.path.exists(self.queue_backup_file):
                with open(self.queue_backup_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.info(f"Queue data loaded from {self.queue_backup_file}")
                return data
            else:
                logger.info(f"No saved queue data found at {self.queue_backup_file}")
                return {}
        except Exception as e:
            logger.error(f"Error loading queue data: {str(e)}")
            return {}

    def delete_rows(self, current_data, selected_rows, column_defs):
        # 선택된 행의 ID를 추출
        selected_ids = [row.get("_id") for row in selected_rows if row.get("_id")]

        # 선택된 행을 제외한 데이터만 유지
        updated_data = [row for row in current_data if row.get("_id") not in selected_ids]

        # 백업 데이터 업데이트
        backup_data = {"rowData": updated_data, "columnDefs": column_defs}
        self.save_queue_data(backup_data)

        return updated_data, backup_data

    def create_column_defs(self, row_data, imported_columns=None):
        if not row_data:
            return []
        columnDefs = [{"field": "_id", "hide": True, "suppressExport": True}]
        columnDefs.append({"field": "APPLICATION", "headerName": "APPLICATION", "pinned": "left", "checkboxSelection": True, "headerCheckboxSelection": True, "editable": False})
        columnDefs.append(
            {
                "field": "JOBNAME",
                "headerName": "JOBNAME",
                "pinned": "left",
            }
        )

        # 컬럼 정의할 필드 목록 생성
        fields = set(key for row in row_data for key in row.keys())
        fields.discard("_id")
        fields.discard("APPLICATION")
        fields.discard("JOBNAME")
        if "CONDITIONAL_FLOW" in fields:
            columnDefs.append(
                {
                    "field": "CONDITIONAL_FLOW",
                    "headerName": "CONDITIONAL_FLOW",
                    "pinned": "left",
                }
            )
            fields.discard("CONDITIONAL_FLOW")

        pvt_columns = ["PROCESS", "VOLTAGE", "TEMPERATURE"]

        if imported_columns:
            ordered_fields = []
            for col in pvt_columns:
                if col in fields and col in imported_columns:
                    ordered_fields.append(col)
                    fields.remove(col)
            for col in imported_columns:
                if col in fields:
                    ordered_fields.append(col)
                    fields.remove(col)
            ordered_fields.extend(sorted(fields))
        else:
            ordered_fields = []
            for col in pvt_columns:
                if col in fields:
                    ordered_fields.append(col)
                    fields.remove(col)
            ordered_fields.extend(sorted(fields))

        for field in ordered_fields:
            columnDefs.append(
                {
                    "field": field,
                    "headerName": field,
                    # 다른 컬럼에는 툴팁 필드와 컴포넌트 지정하지 않음
                }
            )

        return columnDefs

    def extract_corner(self, job_data):
        pvt_keys = ["PROCESS", "VOLTAGE", "TEMPERATURE"]
        has_corner = any(key in job_data for key in pvt_keys)
        if not has_corner:
            return None
        corner = {key: job_data.get(key, "") for key in pvt_keys}
        if not any(corner.values()):
            return None

        return corner

    def extract_inputs(self, job_data):
        exclude_keys = {
            "_id",
            "PROCESS",
            "VOLTAGE",
            "TEMPERATURE",
            "APPLICATION",
            "JOBNAME",
        }
        inputs = {key: value for key, value in job_data.items() if key not in exclude_keys}
        return inputs

    def layout(self):

        saved_queue_data = self.load_queue_data()
        initial_row_data = saved_queue_data.get("rowData", [])
        initial_column_defs = self.create_column_defs(initial_row_data)

        return dmc.Paper(
            children=[
                dmc.Group(
                    [
                        dmc.Title("Job Queue", order=3),
                        dmc.Text("Manage and run multiple jobs", c="dimmed", size="sm"),
                    ],
                    mb="md",
                ),
                dmc.Stack(
                    [
                        html.Div(
                            [
                                dmc.Grid(
                                    [
                                        dmc.GridCol(
                                            dmc.Group(
                                                dbpc.ButtonGroup(
                                                    [
                                                        dbpc.Button(
                                                            "Copy Selected",
                                                            id="copy-selected-button",
                                                            icon="duplicate",
                                                            small=True,
                                                        ),
                                                        dbpc.Button(
                                                            "Delete Selected",
                                                            id="delete-button",
                                                            icon="trash",
                                                            small=True,
                                                        ),
                                                        dbpc.Button(
                                                            "Export CSV",
                                                            id="export-button",
                                                            icon="export",
                                                            small=True,
                                                        ),
                                                        dcc.Upload(
                                                            id="import-upload",
                                                            children=dbpc.Button(
                                                                "Import CSV",
                                                                id="import-button",
                                                                icon="import",
                                                                small=True,
                                                            ),
                                                            multiple=False,
                                                        ),
                                                        dbpc.Button(
                                                            "Edit Input",
                                                            id="edit-selected-button",
                                                            icon="edit",
                                                            small=True,
                                                        ),
                                                        dbpc.Button(
                                                            "Find & Replace",
                                                            id="find-replace-collapse-button",
                                                            icon="edit",
                                                            small=True,
                                                        ),
                                                    ]
                                                ),
                                                align="flex-start",
                                            ),
                                            span=6,
                                        ),
                                        dmc.GridCol(
                                            dmc.Group(
                                                dbpc.ButtonGroup(
                                                    [
                                                        dbpc.Button(
                                                            icon="horizontal-inbetween",
                                                            id="auto-size-btn",
                                                            small=True,
                                                            active=False,
                                                        ),
                                                        dbpc.Button(
                                                            icon="rect-width",
                                                            id="size-to-fit-btn",
                                                            small=True,
                                                            active=True,
                                                        ),
                                                    ]
                                                ),
                                                justify="flex-end",
                                            ),
                                            span=6,
                                        ),
                                    ]
                                ),
                                dbpc.OverlayToaster(id="toaster", position="bottom_left"),
                                dbpc.Collapse(
                                    id="find-replace-collapse",
                                    children=[
                                        dcc.Input(
                                            id="csv-find-input",
                                            placeholder="(ex: R30)",
                                        ),
                                        dcc.Input(
                                            id="csv-replace-input",
                                            placeholder="(ex: R50)",
                                        ),
                                        html.Button(
                                            "Replace",
                                            id="csv-replace-btn",
                                        ),
                                        html.Div(id="csv-replace-result"),
                                    ],
                                ),
                                dag.AgGrid(
                                    id="queue-table",
                                    columnDefs=initial_column_defs,
                                    rowData=initial_row_data,
                                    defaultColDef={
                                        "resizable": True,
                                        "sortable": True,
                                        "filter": True,
                                        "editable": True,
                                    },
                                    selectedRows=[],
                                    style={"height": 300},
                                    enableEnterpriseModules=True,
                                    csvExportParams={"fileName": "JobTable.csv"},
                                    dashGridOptions={
                                        "rowHeight": 24,
                                        "headerHeight": 30,
                                        "rowSelection": "multiple",
                                        "suppressRowClickSelection": True,
                                        "enableRangeSelection": True,
                                        "undoRedoCellEditing": True,
                                    },
                                ),
                            ]
                        ),
                        dbpc.Button("Run All Jobs", id="run-queue-btn", intent="success"),
                    ]
                ),
                # 숨겨진 데이터 저장소 추가
                dcc.Store(id="queue-table-backup", data={"rowData": [], "columnDefs": []}),
            ],
            shadow="sm",
            p="md",
            withBorder=True,
            mt="xl",
        )

    def _register_queue_table_action_callbacks(self, app):
        @app.callback(
            [
                Output("queue-table", "rowData", allow_duplicate=True),
                Output("queue-table", "columnDefs", allow_duplicate=True),
            ],
            Input("copy-selected-button", "n_clicks"),
            [
                State("queue-table", "rowData"),
                State("queue-table", "selectedRows"),
                State("queue-table", "columnDefs"),
            ],
            prevent_initial_call=True,
        )
        def copy_selected_rows(n_clicks, current_data, selected_rows, current_cols):
            if not n_clicks or not selected_rows:
                raise exceptions.PreventUpdate
            new_rows = []
            for row in selected_rows:
                new_row = row.copy()
                new_row["_id"] = str(uuid.uuid4())
                new_rows.append(new_row)
            new_data = current_data.copy() if current_data else []
            new_data.extend(new_rows)
            return new_data, current_cols

        @app.callback(
            Output("queue-table", "deleteSelectedRows", allow_duplicate=True),
            Output("delete-table-backup", "data", allow_duplicate=True),
            Input("delete-button", "n_clicks"),
            State("queue-table", "rowData"),
            State("queue-table", "selectedRows"),
            State("queue-table", "columnDefs"),
            prevent_initial_call=True,
        )
        def delete_selected_rows(n_clicks, current_data, selected_rows, column_defs):
            if not n_clicks or not selected_rows:
                raise exceptions.PreventUpdate
            return self.delete_rows(current_data, selected_rows, column_defs)

        @app.callback(
            Output("queue-table", "exportDataAsCsv"),
            Input("export-button", "n_clicks"),
            State("queue-table", "rowData"),
            prevent_initial_call=True,
        )
        def export_csv(n_clicks, row_data):
            if not n_clicks and not row_data:
                raise exceptions.PreventUpdate
            return True

        @app.callback(
            [
                Output("queue-table", "rowData", allow_duplicate=True),
                Output("queue-table", "columnDefs", allow_duplicate=True),
            ],
            Input("import-upload", "contents"),
            prevent_initial_call=True,
        )
        def import_csv(contents):
            if not contents:
                raise exceptions.PreventUpdate
            try:
                content_type, content_string = contents.split(",")
                decoded = base64.b64decode(content_string)
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                original_columns = df.columns.tolist()
                csv_data = []
                for row in df.to_dict("records"):
                    row["_id"] = str(uuid.uuid4())
                    csv_data.append(row)
                new_column_defs = self.create_column_defs(csv_data, original_columns)

                return csv_data, new_column_defs

            except Exception as e:
                print(f"Error importing CSV: {e}")
                raise exceptions.PreventUpdate

    def _register_callbacks(self, app):
        self._register_queue_table_action_callbacks(app)

        @app.callback(
            Output("auto-size-btn", "active"),
            Output("size-to-fit-btn", "active"),
            Output("queue-table", "columnSize"),
            Input("auto-size-btn", "n_clicks"),
            Input("size-to-fit-btn", "n_clicks"),
            State("auto-size-btn", "active"),
            State("size-to-fit-btn", "active"),
        )
        def update_column_size(auto_clicks, fit_clicks, is_auto_active, is_fit_active):
            if not auto_clicks and not fit_clicks:
                raise exceptions.PreventUpdate

            button_clicked = ctx.triggered_id
            if button_clicked == "auto-size-btn":
                return False, True, "sizeToFit"
            else:
                return True, False, "autoSize"

        @app.callback(
            Output("queue-table-backup", "data", allow_duplicate=True),
            [Input("queue-table", "rowData"), Input("queue-table", "columnDefs"), Input("queue-table", "cellValueChanged")],
            prevent_initial_call=True,
        )
        def backup_queue_data(row_data, column_defs, updated_cell):
            if not row_data or not column_defs:
                return no_update

            backup_data = {"rowData": row_data, "columnDefs": column_defs}
            self.save_queue_data(backup_data)
            return backup_data

        @app.callback(
            Output("queue-table", "columnSize", allow_duplicate=True),
            Input("queue-table", "columnDefs"),
            State("auto-size-btn", "active"),
            prevent_initial_call=True,
        )
        def update_queue_column_settings(column_defs, autosize_active):
            if not column_defs:
                return no_update
            if autosize_active:
                return "autoSize"
            else:
                return "sizeToFit"

        @callback(
            [Output("queue-table", "rowData", allow_duplicate=True), Output("csv-replace-result", "children")],
            [Input("csv-replace-btn", "n_clicks")],
            [State("csv-find-input", "value"), State("csv-replace-input", "value"), State("queue-table", "rowData")],
            prevent_initial_call=True,
        )
        def replace_in_csv(n_clicks, find_text, replace_text, current_data):
            if not n_clicks or not find_text or not current_data:
                return current_data, ""

            updated_data = []
            total_replacements = 0

            for row in current_data:
                new_row = {}
                for key, value in row.items():
                    if isinstance(value, str) and find_text in value:
                        new_value = value.replace(find_text, replace_text or "")
                        new_row[key] = new_value
                        total_replacements += value.count(find_text)
                    else:
                        new_row[key] = value
                updated_data.append(new_row)

            result_msg = f"total {total_replacements}changed. '{find_text}'->'{replace_text}'"

            return updated_data, result_msg

        @app.callback(
            Output("find-replace-collapse", "isOpen"), Input("find-replace-collapse-btn", "n_clicks"), State("find-replace-collapse", "isOpen"), prevent_initial_call=True
        )
        def change_intent(_, isOpen):
            if isOpen:
                return False
            else:
                return True
```

## File: job_set/page.py
```python
import dash_mantine_components as dmc
import dash_blueprint_components as dbpc

from dash import Input, Output, State, ALL, ctx, exceptions, no_update, dcc

from utils.logger import logger
from job_set.jobCards import JobCards
from job_set.jobInputs import JobInputs
from job_set.jobManager import JobManager
from job_set.jobQueue import JobQueue
from utils.config_loader import ConfigLoader
from utils.sol_constants import IDENTIFIER


class SetPage:
    def __init__(self, app):
        self.config_loader = ConfigLoader()
        self.app_configs = self.config_loader.app_configs
        self.job_cards = JobCards(app, self.config_loader)
        self.job_inputs = JobInputs(app, self.config_loader.app_configs)
        self.job_queue = JobQueue(app)

        self.register_callbacks(app)

    def layout(self):
        """Generate job set page layout"""
        return dmc.Container(
            children=[
                dmc.Paper(
                    children=[
                        dbpc.Button(
                            id="open-setup-collapse",
                            children=dmc.Title("Job Setup", order=2),
                            minimal=True,
                        ),
                        dbpc.Collapse(
                            id="setup-collapse",
                            children=[
                                dmc.Space(h=10),
                                dmc.Grid(
                                    children=[
                                        dmc.GridCol(self.job_cards.layout(), span=4),
                                        dmc.GridCol(self.job_inputs.layout(), span=8),
                                    ],
                                    gutter="xl",
                                ),
                            ],
                            className="bp5-code-block",
                        ),
                        self.job_queue.layout(),
                        dbpc.Alert(
                            children="작성 중인 Application inputs에 값이 덮어쓰기 될 수 있습니다. 선택한 행을 수정하시겠습니까?",
                            id="edit-queuerow-alert",
                            cancelButtonText="Cancel",
                            confirmButtonText="Edit row",
                            icon="changes",
                            intent="success",
                        ),
                    ],
                    p="lg",
                    shadow="xs",
                    withBorder=True,
                ),
                dcc.Store(id="config-loader-refresh"),
            ],
            size="xl",
            fluid=True,
        )

    def _validate_app_selection(self, signoff_apps):
        """Application 선택 상태 검증"""
        return signoff_apps and None not in signoff_apps

    def _validate_pvt_settings(self, signoff_apps, PVTs):
        """PVT 설정이 필요한 application의 PVT 값 검증"""
        for i, app in enumerate(signoff_apps):
            if not app:
                continue
            app_config = self.app_configs.get(app, {})

            if not app_config.get("pvt_inputs", False):
                continue

            # PVT가 필요한데 입력이 없는 경우
            if not PVTs[i]:
                logger.debug(f"PVT required for {app} but no PVT input provided")
                return False

            # 각 PVT row 검증
            for pvt_row in PVTs[i]:
                try:
                    pvt_values = self._extract_pvt_values(pvt_row)
                    if not all(pvt_values.values()):
                        logger.debug(f"Incomplete PVT values for {app}: {pvt_values}")
                        return False
                except Exception as e:
                    logger.error(f"Error validating PVT row: {str(e)}")
                    return False

        return True

    def _validate_required_inputs(self, input_values, signoff_apps, pvt_containers):
        """필수 입력값이 모두 채워져 있는지 검증 PVT 조건에 따라 필요한 입력만 검증"""

        required_inputs = {"file": {}, "fileselect": {}, "number": {}, "text": {}, "textarea": {}, "select": {}, "multiselect": {}, "checkbox": {}}

        for app_name in signoff_apps:
            if not app_name:
                continue
            app_config = self.app_configs.get(app_name, {})
            for input_config in app_config.get("inputs", []):
                if input_config.get("required", True):
                    input_type = input_config["type"].split("_")[0]  # file_input -> file
                    input_name = input_config["name"].replace("_", "-")
                    required_inputs[input_type][input_name] = input_config

        for i, app_name in enumerate(signoff_apps):
            if not app_name:
                continue

            # PVT가 true인 application인 경우
            app_config = self.app_configs.get(app_name, {})
            if not app_config:
                continue

            if app_config.get("pvt_inputs", False):
                pvt_settings = self._extract_pvt_values(pvt_containers[i][0])
                # 각 input type 검증
                for input_type, required_fields in required_inputs.items():
                    for input_name, input_config in required_fields.items():
                        # pvt_conditioned_settings에 대해서만 PVT 의존성 검사
                        if input_config.get("depends_on"):
                            # PVT 의존성 확인
                            depends_on = input_config["depends_on"]
                            should_check = True

                            # PVT 조건별로 의존성 확인
                            for pvt_type, required_value in depends_on.items():
                                if pvt_settings[pvt_type] != required_value:
                                    should_check = False
                                    break

                            # 의존성 조건이 맞지 않으면 해당 입력은 검증하지 않음
                            if not should_check:
                                continue

                        # 입력값 검증
                        if input_name not in input_values[input_type] or not input_values[input_type][input_name]:
                            logger.debug(f"Required {input_type} input '{input_name}' is missing")
                            return False

            else:
                for input_type, required_fields in required_inputs.items():
                    for input_name in required_fields:
                        if input_type == "checkbox":
                            if input_name not in input_values[input_type]:
                                logger.debug(f"Required {input_type} input {input_name} is missing")
                                return False
                        elif input_name not in input_values[input_type] or not input_values[input_type][input_name]:
                            logger.debug(f"Required {input_type} input '{input_name}' is missing")
                            return False
        return True

    def _unified_validation(self, signoff_apps, PVTs, input_values):
        """통합 검증 프로세스"""
        validation_steps = [
            self._validate_app_selection(signoff_apps),
            self._validate_pvt_settings(signoff_apps, PVTs),
            self._validate_required_inputs(input_values, signoff_apps, PVTs),
        ]
        return all(validation_steps)

    def _collect_input_values(self, file_inputs, file_selects, number_inputs, text_inputs, textarea_inputs, select_inputs, multiselect_inputs, checkbox_inputs):
        """모든 입력값을 수집하여 dictionary 형태로 반환"""
        input_values = {
            "file": {},
            "fileselect": {},
            "number": {},
            "text": {},
            "textarea": {},
            "select": {},
            "multiselect": {},
            "checkbox": {},
        }

        # File inputs
        for i, value in enumerate(file_inputs):
            input_id = ctx.inputs_list[5][i]["id"]["index"]
            input_values["file"][input_id] = value

        # File select inputs
        for i, value in enumerate(file_selects):
            input_id = ctx.inputs_list[6][i]["id"]["index"]
            input_values["fileselect"][input_id] = value

        # Number inputs
        for i, value in enumerate(number_inputs):
            input_id = ctx.inputs_list[7][i]["id"]["index"]
            input_values["number"][input_id] = value

        # Text inputs
        for i, value in enumerate(text_inputs):
            input_id = ctx.inputs_list[8][i]["id"]["index"]
            input_values["text"][input_id] = value

        # Textarea inputs
        for i, value in enumerate(textarea_inputs):
            input_id = ctx.inputs_list[9][i]["id"]["index"]
            input_values["textarea"][input_id] = value

        # Select inputs
        for i, value in enumerate(select_inputs):
            input_id = ctx.inputs_list[10][i]["id"]["index"]
            input_values["select"][input_id] = value

        # Multiselect inputs
        for i, value in enumerate(multiselect_inputs):
            input_id = ctx.inputs_list[11][i]["id"]["index"]
            input_values["multiselect"][input_id] = value

        # Checkbox Inputs
        for i, value in enumerate(checkbox_inputs):
            input_id = ctx.inputs_list[12][i]["id"]["index"]
            input_values["checkbox"][input_id] = value

        return input_values

    def _extract_pvt_values(self, pvt_row):
        """PVT row에서 process, voltage, temperature 값 추출"""
        return {
            "PROCESS": pvt_row["props"]["children"][0]["props"]["value"],
            "VOLTAGE": pvt_row["props"]["children"][1]["props"]["value"],
            "TEMPERATURE": pvt_row["props"]["children"][2]["props"]["value"],
        }

    def register_callbacks(self, app):
        @app.callback(
            Output("job-count-indicator", "label", allow_duplicate=True),
            Output("job-count-indicator", "disabled", allow_duplicate=True),
            Input({"type": "multiselect-input", "index": ALL}, "value"),
            Input({"type": "pvt-container", "index": ALL}, "children"),
            Input({"type": "checkgroup-flow", "index": ALL}, "value"),
            prevent_initial_call=True,
        )
        def update_job_counter_to_add_queue(multiselect_values, pvt_container, flows):
            total_pvt_jobs = 0
            for i, pvts in enumerate(pvt_container):
                if len(flows) > i and flows[i]:
                    total_pvt_jobs += len(pvts) * len(flows[i])
                else:
                    total_pvt_jobs += len(pvts)

            total_subckt_jobs = 0
            for i, values in enumerate(multiselect_values):
                if ctx.inputs_list[0][i]["id"]["index"] == "Top-Subckt" and values:
                    for v in values:
                        if v:
                            total_subckt_jobs += 1
                    break
            total_jobs = 0
            if total_subckt_jobs == 0:
                total_jobs = total_pvt_jobs
            else:
                total_jobs = total_pvt_jobs * total_subckt_jobs

            return f"{total_jobs} jobs", False if total_jobs else True

        @app.callback(
            Output("add-jobs-btn", "disabled"),
            Input({"type": "signoff-app-select", "index": ALL}, "value"),
            Input({"type": "pvt-container", "index": ALL}, "children"),
            Input({"type": "select-process", "index": ALL, "row": ALL}, "value"),
            Input({"type": "select-voltage", "index": ALL, "row": ALL}, "value"),
            Input({"type": "select-temperature", "index": ALL, "row": ALL}, "value"),
            Input({"type": "file-input-text", "index": ALL, "flow": ALL}, "value"),
            Input({"type": "file-select-input", "index": ALL, "flow": ALL}, "value"),
            Input({"type": "number-input", "index": ALL, "flow": ALL}, "value"),
            Input({"type": "text-input", "index": ALL, "flow": ALL}, "value"),
            Input({"type": "textarea-input", "index": ALL, "flow": ALL}, "value"),
            Input({"type": "select-input", "index": ALL, "flow": ALL}, "value"),
            Input({"type": "multiselect-input", "index": ALL, "flow": ALL}, "value"),
            Input({"type": "checkbox-input", "index": ALL, "flow": ALL}, "value"),
            prevent_initial_call=True,
        )
        def check_add_job_queue_button_status(
            signoff_values,
            PVTs,
            process_inputs,
            voltage_inputs,
            temperature_inputs,
            file_inputs,
            file_selects,
            number_inputs,
            text_inputs,
            textarea_inputs,
            select_inputs,
            multiselect_inputs,
            checkbox_inputs,
        ):
            """Run 버튼의 활성화 상태를 결정하는 콜백"""
            # 고유 식별자에서 실제 앱 이름으로 변환
            signoff_apps = []
            for val in signoff_values:
                if val is None:
                    continue

                if IDENTIFIER in val:
                    app_name = val.split(IDENTIFIER, 1)[1]
                else:
                    app_name = val

                signoff_apps.append(app_name)

            input_values = self._collect_input_values(
                file_inputs,
                file_selects,
                number_inputs,
                text_inputs,
                textarea_inputs,
                select_inputs,
                multiselect_inputs,
                checkbox_inputs,
            )
            if not self._unified_validation(signoff_apps, PVTs, input_values):
                return True
            return False

        @app.callback(
            Output("queue-table", "columnDefs", allow_duplicate=True),
            Output("queue-table", "rowData", allow_duplicate=True),
            Output("creating-jobs-container", "children", allow_duplicate=True),
            Output("edit-from-queue", "data", allow_duplicate=True),
            Input("add-jobs-btn", "n_clicks"),
            State({"type": "signoff-app-select", "index": ALL}, "value"),
            State({"type": "pvt-container", "index": ALL}, "children"),
            State({"type": "file-input-text", "index": ALL, "flow": ALL}, "value"),
            State({"type": "file-select-text", "index": ALL, "flow": ALL}, "value"),
            State({"type": "number-input", "index": ALL, "flow": ALL}, "value"),
            State({"type": "text-input", "index": ALL, "flow": ALL}, "value"),
            State({"type": "textarea-input", "index": ALL, "flow": ALL}, "value"),
            State({"type": "select-input", "index": ALL, "flow": ALL}, "value"),
            State({"type": "multiselect-input", "index": ALL, "flow": ALL}, "value"),
            State({"type": "checkbox-input", "index": ALL, "flow": ALL}, "checked"),
            State({"type": "checkgroup-flow", "index": ALL}, "children"),
            State("queue-table", "rowData"),
            prevent_initial_call=True,
        )
        def add_jobs(
            n_clicks,
            signoff_values,
            pvt_splits,
            file_inputs,
            file_selects,
            number_inputs,
            text_inputs,
            textarea_inputs,
            select_inputs,
            multiselect_inputs,
            checkbox_inputs,
            conditional_flow_children,
            existing_data,
        ):
            if not n_clicks:
                raise exceptions.PreventUpdate

            # 고유 식별자에서 실제 앱 이름으로 변환
            signoff_apps = []
            for val in signoff_values:
                if val is None:
                    continue

                if "_" in val:
                    app_name = val.split("_", 1)[1]
                else:
                    app_name = val

                signoff_apps.append(app_name)

            # 입력값들을 dictionary로 변환
            input_values = {}

            def _append_input_values(id, input_type, value, flow, input_values_dict):
                if id in input_values_dict:
                    input_values_dict[id].append({"type": input_type, "value": value, "flow": flow})
                else:
                    input_values_dict[id] = [{"type": input_type, "value": value, "flow": flow}]

            for i, file_input in enumerate(file_inputs):
                input_id = ctx.states_list[2][i]["id"]["index"]
                input_flow = ctx.states_list[2][i]["id"]["flow"]
                _append_input_values(input_id, "file", file_input, input_flow, input_values)

            for i, file_select in enumerate(file_selects):
                input_id = ctx.states_list[3][i]["id"]["index"]
                input_flow = ctx.states_list[3][i]["id"]["flow"]
                _append_input_values(input_id, "fileselect", file_select, input_flow, input_values)

            for i, number_input in enumerate(number_inputs):
                input_id = ctx.states_list[4][i]["id"]["index"]
                input_flow = ctx.states_list[4][i]["id"]["flow"]
                _append_input_values(input_id, "number", number_input, input_flow, input_values)

            for i, text_input in enumerate(text_inputs):
                input_id = ctx.states_list[5][i]["id"]["index"]
                input_flow = ctx.states_list[5][i]["id"]["flow"]
                _append_input_values(input_id, "text", text_input, input_flow, input_values)

            for i, textarea_input in enumerate(textarea_inputs):
                input_id = ctx.states_list[6][i]["id"]["index"]
                input_flow = ctx.states_list[6][i]["id"]["flow"]
                _append_input_values(input_id, "textarea", textarea_input, input_flow, input_values)

            for i, select_input in enumerate(select_inputs):
                input_id = ctx.states_list[7][i]["id"]["index"]
                input_flow = ctx.states_list[7][i]["id"]["flow"]
                _append_input_values(input_id, "select", select_input, input_flow, input_values)

            for i, multiselect_input in enumerate(multiselect_inputs):
                input_id = ctx.states_list[8][i]["id"]["index"]
                input_flow = ctx.states_list[8][i]["id"]["flow"]
                _append_input_values(input_id, "multiselect", multiselect_input, input_flow, input_values)

            for i, checkbox_input in enumerate(checkbox_inputs):
                input_id = ctx.states_list[9][i]["id"]["index"]
                input_flow = ctx.states_list[9][i]["id"]["flow"]
                _append_input_values(input_id, "checkbox", checkbox_input, input_flow, input_values)

            # 각 Job Card별로 작업 생성
            for i, app_name in enumerate(signoff_apps):
                if not app_name:
                    continue

                try:
                    app_config = self.app_configs.get(app_name, {})
                    if not app_config:
                        continue

                    is_pvt_required = app_config.get("pvt_inputs", False)

                    """PVT 코너 정보 추출"""
                    corners = []
                    if is_pvt_required and pvt_splits[i]:
                        for pvt_row in pvt_splits[i]:
                            try:
                                corners.append(
                                    {
                                        "PROCESS": pvt_row["props"]["children"][0]["props"]["value"],
                                        "VOLTAGE": pvt_row["props"]["children"][1]["props"]["value"],
                                        "TEMPERATURE": pvt_row["props"]["children"][2]["props"]["value"],
                                    }
                                )
                            except (KeyError, IndexError) as e:
                                logger.error(f"잘못된 PVT 형식: {pvt_row}")
                                continue
                    else:
                        corners = [None]  # PVT가 필요없는 경우 None으로 하나만 생성

                    """앱 설정에 따라 입력값 준비"""
                    job_inputs = {}
                    for input_config in app_config.get("inputs", []) + app_config.get("pvt_inputs", []):
                        input_name = input_config["name"].replace("_", "-")
                        if input_name in input_values:
                            value = input_values[input_name]["value"]
                            # 입력값 타입 변환 (예: 숫자 입력 처리)
                            if input_config["type"] == "number_input" and value:
                                value = float(value)
                            job_inputs[input_config["name"].upper()] = value

                    """서브회로 리스트 처리"""
                    subckt_list = [""]  # 기본값
                    if "Top_Subckt" in job_inputs:
                        subckts = job_inputs["Top_Subckt"]
                        subckt_list = subckts if isinstance(subckts, list) else [subckts]

                    for subckt in subckt_list:
                        if subckt:
                            job_inputs["Top_Subckt"] = subckt

                        # 각 corner별로 작업 디렉토리 생성
                        for corner in corners:
                            # Conditional input flows 에 따라 job_inputs 추가
                            conditional_input_flow = app_config.get("conditional_input_flow", [])
                            if conditional_flow_children[i]:
                                all_unchecked = True
                                for child in conditional_flow_children[i]:
                                    child_value = child["props"].get("value")
                                    child_checked = child["props"].get("checked", False)
                                    if not child_checked:
                                        continue
                                    all_unchecked = False
                                    conditional_inputs = {}
                                    for condition in conditional_input_flow:
                                        flow_names = condition.get("flow_names")
                                        if flow_names and child_value in flow_names:
                                            condition_name = condition.get("name").replace("_", "-")
                                            input_flows = input_values[condition_name]
                                            for input_flow in input_flows:
                                                if input_flow.get("flow", "") == child_value:
                                                    conditional_inputs[condition["name"]] = input_flow["value"]
                                    new_row = self.job_queue.parse_job_data(app_name, corner, job_inputs, child_value, conditional_inputs)
                                    existing_data = existing_data + [new_row]

                                if all_unchecked:
                                    new_row = self.job_queue.parse_job_data(app_name, corner, job_inputs)
                                    existing_data = existing_data + [new_row]
                            else:
                                try:
                                    new_row = self.job_queue.parse_job_data(app_name, corner, job_inputs)
                                    existing_data = existing_data + [new_row]

                                except Exception as e:
                                    logger.error(f"{app_name} 작업 생성 실패: {str(e)}", exc_info=True)
                                    continue
                except Exception as e:
                    logger.error(f"{app_name} 처리 중 에러 발생: {str(e)}", exc_info=True)
                    continue

            updated_cols = self.job_queue.create_column_defs(existing_data)
            return updated_cols, existing_data, []

        @app.callback(
            Output("queue-table", "rowData", allow_duplicate=True),
            Output("queue-table-backup", "data", allow_duplicate=True),
            Output("job-created-alert", "isOpen"),
            Output("job-created-alert", "children"),
            Input("run-queue-btn", "n_clicks"),
            State("queue-table", "rowData"),
            State("queue-table", "selectedRows"),
            State("queue-table", "columnDefs"),
            prevent_initial_call=True,
        )
        def run_queue(n_clicks, queue_data, selected_rows, column_defs):
            if not n_clicks or not selected_rows:
                return no_update, no_update, False, no_update
            # Queue의 작업의 유효성 검사
            job_queue = []
            current_data = queue_data
            for job in selected_rows:
                try:
                    jobs = JobManager(
                        app_name=job["APPLICATION"],
                        subckt=job.get("Top_Subckt"),
                        job_name=job.get("JOBNAME"),
                        conditional_flow=job.get("CONDITIONAL_FLOW"),
                        corner=self.job_queue.extract_corner(job),
                        inputs=self.job_queue.extract_inputs(job),
                    )
                    job_queue.append(jobs)
                except Exception as e:
                    logger.error(f"{job['APPLICATION']} 작업 생성 실패: {str(e)}", exc_info=True)
                    continue
            current_data, backup_datas = self.job_queue.delete_rows(current_data, selected_rows, column_defs)
            # Queue의 모든 작업을 병렬로 실행
            for job in job_queue:
                try:
                    job.setup()
                    job.run()

                except Exception as e:
                    logger.error(f"{job['APPLICATION']} 작업 생성 실패: {str(e)}", exc_info=True)
                    continue
            return current_data, backup_datas, True, f"Created and started jobs"  # 작업 생성 후 job card 컨테이너 비우기

        @app.callback(
            Output("config-loader-refresh", "data", allow_duplicate=True),
            Input("config-loader-refresh", "data"),
            prevent_initial_call=True,
        )
        def refresh_configs(data):
            if data:
                self.config_loader.refresh()
                self.job_inputs.update_app_config(self.config_loader.app_configs)
            return False
```

## File: RUNSCRIPTS/DSC/input_config.yaml
```yaml
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

## File: RUNSCRIPTS/DSC/make_csv.py
```python
import sys
import csv
from pathlib import Path


def convert_dsc_output_to_csv(input_file):
    try:
        input_path = Path(input_file)
        output_path = input_path.with_suffix(".csv")

        print(f"Converting {input_path} to CSV format...")

        with open(input_path, "r") as infile, open(output_path, "w", newline="") as outfile:
            writer = csv.writer(outfile)

            # 첫 번째 데이터 행을 찾아서 필드 개수 파악
            for line in infile:
                fields = line.strip().split()
                if fields and "----------" not in line:
                    expected_fields = len(fields)
                    break

            # 파일 포인터를 처음으로 되돌림
            infile.seek(0)

            # 데이터 처리
            for line in infile:
                fields = line.strip().split()

                # 구분선이나 빈 줄 스킵
                if not fields or "----------" in line:
                    continue

                # 필드 개수가 일치하는 경우만 처리
                if len(fields) == expected_fields:
                    writer.writerow(fields)
                else:
                    print(f"Warning: Skipping malformed line: {line.strip()}")

        print(f"Successfully created: {output_path}")
        return str(output_path)

    except Exception as e:
        print(f"Error converting file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <dsc_output_file>")
        sys.exit(1)

    convert_dsc_output_to_csv(sys.argv[1])
```

## File: RUNSCRIPTS/DSC/netlist_preprocessing.py
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
        return (
            line.replace(" / ", " ")
            .replace(" ( ", " ")
            .replace(" ) ", " ")
            .replace(" )\n", "\n")
            .replace("[", "<")
            .replace("]", ">")
            .replace("!", "_")
            .replace("(", "_")
            .replace(")", "_")
            .replace("|", "_")
            .replace("#", "_")
            .replace("\\", "_")
        )

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
        etc_lines = []  # comments, ...

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
        """SUBCKT 정의를 의존성에 따라 정렬"""
        dependency_graph = defaultdict(set)

        # 그래프 생성: subckt 간 의존성 정의
        for subckt_name, subckt_lines in subckt_definitions.items():
            for line in subckt_lines:
                if line.lower().startswith("x"):  # instance call
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
            result_lines.append("")  # 서브서킷 간 빈 줄
        # 호출 부분 출력
        result_lines.extend(subckt_calls)
        result_lines.append("")  # 마지막 줄 개행
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
    parser = argparse.ArgumentParser(
        description="Reorder SPICE netlist by arranging .subckt definitions before instance calls. Convert char into a format readable by SPACE syntax."
    )
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

## File: RUNSCRIPTS/DSC/pre_setting.py
```python
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

## File: RUNSCRIPTS/DSC/run.sh
```bash
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

## File: RUNSCRIPTS/DSC/run.tcl
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

## File: RUNSCRIPTS/LS/input_config.yaml
```yaml
Level_Shifter_Check: 
  color: "#4263eb"
  description: "LS"
  group: "Static Signoff"
  inputs:
    - name: SPC_Netlist_File_for_ls
      type: file_input
      required: true 
      default: "/user/l432gxr80/VERIFY/SIGNOFF/2_PEC/R50/XR_FULLCHIP_R50.spc"
      description: "Circuit netlist file in SPICE format"
    
    - name: Blkstar_File
      type: file_input
      required: true
      default: "/user/l432gxr02/VERIFY/BLKSTAR_R20/STAR/xr_pad_231128.star"
      description: "Star file containing layout star connectivity information"
    
    - name: EDR_File  
      type: file_input
      required: true
      default: "/user/l432gxr00/PARAM/LINK/Zenith_XR_EDR"
      description: "EDR file for defining extra device rules"
    
    - name: MP_File
      type: file_input  
      required: true
      default: "/user/l432gxr00/PARAM/LINK/Zenith_XR_MP"
      description: "Model parameter file defining simulation models"
      
    - name: Top_Subckt 
      type: text_input
      required: false
      default: ""
      description: "Top-level subcircuit name (optional, if not specified uses the netlist top subcircuit)"
    - name: Default_Voltage
      type: number_input
      required: true
      unit: "V"
      default: -0.96
      description: "Default voltage value for undefined nodes"

    - name: Input_Slope
      type: number_input
      unit: "ns"
      required: true
      unit: "ns"
      default: 0.4 
      description: "Input signal transition time (ns)"
      
    - name: Simulation_Time
      type: number_input
      unit: "ns"
      required: true
      default: 10
      description: "Total simulation time period (ns)"
      
    - name: Simulation_Time_Step
      unit: "ns"
      type: number_input
      required: true
      default: 0.01
      description: "Time step for simulation (ns)"

    - name: UserDefine_Corner
      type: text_input
      required: false  
      default: ""
      description: "Custom simulation corner specification (optional)"
```

## File: RUNSCRIPTS/LS/run.sh
```bash
#!/bin/csh -f

set UPDATE_CONFIG = /user/signoff.dev/launcher/utils/update_config



# Initialize
$UPDATE_CONFIG --start --msg "preprocessing"


# Preprocessing
python pre_setting.py
if ($status != 0) then
    $UPDATE_CONFIG  --fail --msg "Preprocessing failed"
    exit 1
endif


# Main simulation
$UPDATE_CONFIG --msg "Running simulation"
space_sub -Is -cpu 8 -mem 300000 -scv run.tcl
if ($status != 0) then
    $UPDATE_CONFIG --fail --msg "Simulation failed"
    exit 1
endif

# Postprocessing
$UPDATE_CONFIG --msg "Postprocessing"
python ls_write_csv.py 
if ($status != 0) then
    $UPDATE_CONFIG --fail --msg "Postprocessing failed"
    exit 1
endif


# Job completed successfully
$UPDATE_CONFIG --done
```

## File: utils/config_loader.py
```python
import os
import re
import yaml
from pathlib import Path
from typing import Dict
from utils.logger import logger
from utils.settings import SIGNOFF_APPLICATION_YAML
from utils.workspace import get_workspace_dir


class ConfigLoader:
    def __init__(self):
        self.refresh()

    def refresh(self):
        self.app_configs = {}
        self.classification_schemes = []
        self._load_configurations()

    def _load_configurations(self):
        try:
            with open(SIGNOFF_APPLICATION_YAML, "r") as f:
                base_config = yaml.safe_load(f)

            # 분류 체계 로드
            self.classification_schemes = base_config.get("classification_schemes", [])

            mp_file, edr_file = self.get_mp_edr_file_path()

            for app in base_config["applications"]:
                app_name = app["name"]
                runscript_path = app["runscript_path"]
                classification = app.get("classification", {})

                config_path = os.path.join(runscript_path, "input_config.yaml")

                if not os.path.exists(config_path):
                    logger.warning(f"Configuration file not found for {app_name}: {config_path}")
                    continue
                with open(config_path, "r") as f:
                    app_config = yaml.safe_load(f)
                    app_config[app_name]["runscript_path"] = runscript_path

                    # 분류 정보 추가
                    app_config[app_name]["classification"] = classification

                    # MP, EDR default value 변경
                    inputs = app_config[app_name].get("inputs")
                    if inputs:
                        if mp_file:
                            MP = next((item for item in inputs if item["name"] == "MP_File"), None)
                            if MP:
                                MP["default"] = mp_file
                        if edr_file:
                            EDR = next((item for item in inputs if item["name"] == "EDR_File"), None)
                            if EDR:
                                EDR["default"] = edr_file

                    self.app_configs.update(app_config)

        except Exception as e:
            logger.error(f"Error loading configurations: {str(e)}")
            raise

    def get_mp_edr_file_path(self):
        workspace_path = Path(get_workspace_dir())
        path_parts = workspace_path.parts

        prefix_regex = r"[a-z]+[0-9]+g"
        match = re.search(prefix_regex, path_parts[2])

        if match:
            product_name = path_parts[2][match.end() : match.end() + 2]
        else:
            return "", ""

        mp_name = product_name.upper() + "_MP"
        edr_name = product_name.upper() + "_EDR"

        if path_parts[2].endswith("00"):
            param_link_path = Path("/").joinpath(path_parts[1], path_parts[2], "PARAM", "LINK")
        else:
            org_project = path_parts[2][:-2] + "00"
            param_link_path = Path("/").joinpath(path_parts[1], org_project, "PARAM", "LINK")

        if not os.path.isdir(param_link_path):
            return "", ""

        mp_file = [file for file in os.listdir(param_link_path) if file.endswith(mp_name)]
        edr_file = [file for file in os.listdir(param_link_path) if file.endswith(edr_name)]

        mp = ""
        edr = ""

        if mp_file:
            mp = os.path.join(param_link_path, mp_file[0])
        if edr_file:
            edr = os.path.join(param_link_path, edr_file[0])

        return mp, edr

    def get_application_names(self):
        return list(self.app_configs.keys())

    def get_app_config(self, app_name: str) -> dict:
        return self.app_configs.get(app_name, {})

    def get_all_configs(self) -> Dict[str, dict]:
        return self.app_configs

    def get_classification_schemes(self):
        return self.classification_schemes

    def get_applications_by_category(self, scheme_key, category_name):
        """특정 분류 체계와 카테고리에 해당하는 애플리케이션 목록 반환"""
        applications = []

        for scheme in self.classification_schemes:
            if scheme["key"] == scheme_key:
                for category in scheme["categories"]:
                    if category["name"] == category_name:
                        applications = category.get("applications", [])
                        break
                break

        # 실제로 존재하는 애플리케이션만 필터링 (input_config.yaml이 있는 것들)
        valid_applications = []
        for app_name in applications:
            if app_name in self.app_configs:
                valid_applications.append(app_name)

        return valid_applications

    def reload_configurations(self):
        self.app_configs.clear()
        self.classification_schemes = []
        self._load_configurations()
```

## File: utils/devworks_api.py
```python
import os
import pwd
import requests


USERNAME = os.getenv("USER", "unknown")
DEVWORKS_URL = "http://dsky2527:7089"
SYSTEM_ID = "sorv"
SYSTEM_PASS = "Lg=="


def get_auth_token():

    url = f"{DEVWORKS_URL}/send/system/authentication"
    payload = {"systemId": SYSTEM_ID, "systemPass": SYSTEM_PASS}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        raise Exception("Failed to get authentication token")


def send_devworks_message(params):

    token = get_auth_token()
    url = f"{DEVWORKS_URL}/api/send"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    # params = ["deepwonwoo", "DSC Signoff Job", "시작", "/user/signoff.dsa/launcher"],

    payload = {
        "msgId": "73fe087f",  # %s님의 %s 이(가) %s 되었습니다.( %s )
        "params": params,
        "sender": pwd.getpwnam(USERNAME).pw_uid,
        "recipients": [pwd.getpwnam(USERNAME).pw_uid],
        "purpose": "Launcher Operation",
        "project": "Launcher",
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to send message: {response.text}")


def send_help_devworks_message():
    token = get_auth_token()
    url = f"{DEVWORKS_URL}/api/send"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    params = [
        USERNAME,
        "SOL 매뉴얼",
        "\n전송( https://confluence.samsungds.net/ )",
        "문의 : DT팀 최원우, 오지은",
    ]

    payload = {
        "msgId": "73fe087f",  # %s님의 %s 이(가) %s 되었습니다.( %s )
        "params": params,
        "sender": pwd.getpwnam(USERNAME).pw_uid,
        "recipients": [pwd.getpwnam(USERNAME).pw_uid],
        "purpose": "Launcher Operation",
        "project": "Launcher",
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to send message: {response.text}")
```

## File: utils/logger.py
```python
import logging
import logging.handlers


def setup_logger(name="Launcher"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d\n%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(f"{name}.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 전역 로거 인스턴스 생성
logger = setup_logger()
```

## File: utils/lsf.py
```python
# from pythonlsf import lsf
from pprint import pprint
import enum
import os

# class JobStat(enum.Enum):
#     PEND = lsf.JOB_STAT_PEND
#     RUN = lsf.JOB_STAT_RUN
#     EXIT = lsf.JOB_STAT_EXIT
#     DONE = lsf.JOB_STAT_DONE


def _convert_job_dict(job_into_ent):
    job_dict = dict()
    job_dict["job_id"] = job_into_ent.jobId
    job_dict["user_name"] = job_into_ent.user
    job_dict["cpuTime"] = job_into_ent.cpuTime
    job_dict["cwd"] = job_into_ent.cwd
    job_dict["jName"] = job_into_ent.jName
    job_dict["jobPid"] = job_into_ent.jobPid
    job_dict["runTime"] = job_into_ent.runTime
    job_dict["subcwd"] = job_into_ent.subcwd
    job_dict["startTime"] = job_into_ent.startTime
    job_dict["runTime"] = job_into_ent.runTime
    job_dict["queue_name"] = job_into_ent.submit.queue
    job_dict["job_status"] = _convert_job_status(job_into_ent.status)
    return job_dict


# def get_lsf_jobs(job_id=0, job_name=None, user_name=lsf.ALL_USERS, queue_name=None, host_name=None, option=lsf.ALL_JOB):
def get_lsf_jobs(
    job_id=0,
    job_name=None,
    user_name=None,
    queue_name=None,
    host_name=None,
    option=None,
):
    return list()
    # if lsf.lsb_init("test") != 0:
    #     raise Exception(lsf.lsb_sysmsg())
    # try:
    #     job_cnt = lsf.lsb_openjobinfo(job_id, job_name, user_name, queue_name, host_name, option)
    #     more = lsf.new_intp()
    #     job_list = list()
    #     for _ in range(job_cnt):
    #         job_info = lsf.lsb_readjobinfo(more)
    #         job_list.append(_convert_job_dict(job_info))
    #     lsf.delete_intp(more)
    #     lsf.lsb_closejobinfo()
    #     return job_list
    # except Exception as e:
    #     print(f"get lsf jobs Error: {e}")
    #     return list()


def _convert_job_status(status):
    return None
    # if status & lsf.JOB_STAT_PEND:
    #     job_status = JobStat.PEND.name
    # elif status & lsf.JOB_STAT_RUN:
    #     job_status = JobStat.RUN.name
    # elif status & lsf.JOB_STAT_EXIT:
    #     job_status = JobStat.EXIT.name
    # elif status & lsf.JOB_STAT_DONE:
    #     job_status = JobStat.DONE.name
    # return job_status


def kill_lsf_jobs(job_ids, signal=9):
    pass

    # signalbulkjobs = lsf.signalBulkJobs()
    # signalbulkjobs.signal = signal
    # signalbulkjobs.njobs = len(job_ids)
    # signalbulkjobs.jobs = lsf.new_LS_LONG_INTArray(len(job_ids))
    # # Set job IDs in the array
    # for i, job_id in enumerate(job_ids):
    #     lsf.LS_LONG_INTArray_setitem(signalbulkjobs.jobs, i, job_id)
    # if lsf.lsb_init("test") > 0:
    #     exit(1)
    # # Kill the specified jobs
    # lsf.lsb_killbulkjobs(signalbulkjobs)
```

## File: utils/manual_link.py
```python
TOOL_MANUAL_MAP = {
    "DSC": "test/dsc",
    # ...
}
```

## File: utils/set_input_env.py
```python
#!/user/signoff.dsa/miniconda3/envs/viewer/bin/python

import yaml
import sys
import os
import argparse


def generate_environment_script(config_file="input_config.yaml"):
    """config 파일을 읽어서 환경변수 설정 스크립트 생성"""
    try:
        # config 파일 존재 확인
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # config 파일 읽기
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # env_setup.csh 스크립트 생성
        script_path = "env_setup.csh"
        with open(script_path, "w", encoding="utf-8") as f:
            # 스크립트 헤더
            f.write("#!/bin/csh -f\n\n")

            f.write("# Environment variables for Signoff Application\n")
            f.write(f"# Generated from {config_file}\n\n")

            f.write(f"setenv PYTHONIOENCODING utf-8\n")
            f.write(f"setenv PYTHONUTF8 1\n")
            f.write(f"setenv PATH /user/signoff.dsa/miniconda3/envs/launcher/bin:$PATH\n\n")

            app_name = next(iter(config.keys()))
            f.write(f"setenv APP {app_name}\n")

            # 첫 번째 application의 설정을 가져옴
            app_config = next(iter(config.values()))

            # Regular inputs 처리
            if "inputs" in app_config:
                f.write("# Regular inputs\n")
                for input_item in app_config["inputs"]:
                    env_name = input_item["name"].upper()
                    default_value = str(input_item.get("default", ""))
                    f.write(f'setenv {env_name} "{default_value}"\n')
                f.write("\n")

            # PVT dependent inputs 처리
            if "pvt_inputs" in app_config:
                f.write("# PVT dependent inputs\n")
                for pvt_input in app_config["pvt_inputs"]:
                    env_name = pvt_input["name"].upper()
                    default_value = str(pvt_input.get("default", ""))
                    f.write(f'setenv {env_name} "{default_value}"\n')

            if "conditional_input_flow" in app_config:
                f.write("# Conditional input flows\n")
                flow_name = ""
                for flow_input in app_config["conditional_input_flow"]:
                    flow_name = flow_input.get("flows")
                    if flow_name:
                        f.write(f'setenv CONDITIONAL_FLOW "{flow_name}"\n')
                        break

                for flow_input in app_config["conditional_input_flow"]:
                    env_name = flow_input.get("name")
                    if not env_name:
                        continue
                    env_flow = flow_input.get("flow_names")
                    if flow_name in env_flow:
                        default_value = str(flow_input.get("default", ""))
                        f.write(f'setenv {env_name.upper()} "{default_value}"\n')

            f.write(f"# For launcher update_config command\n")
            f.write(f"set UPDATE_CONFIG = /user/signoff.dsa/launcher/utils/update_config.py\n")

        # 스크립트에 실행 권한 부여
        os.chmod(script_path, 0o755)
        print(f"Successfully created environment setup script: {script_path}")
        return True

    except Exception as e:
        print(f"Error generating environment script: {str(e)}", file=sys.stderr)
        return False


def main():
    # Command line argument 파싱
    parser = argparse.ArgumentParser(description="Generate environment setup script from config file")
    parser.add_argument("--config", default="input_config.yaml", help="Path to input config yaml file (default: input_config.yaml)")

    args = parser.parse_args()

    # 환경변수 설정 스크립트 생성
    if not generate_environment_script(args.config):
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## File: utils/settings.py
```python
import os
import stat
import shutil
import tempfile


def get_user_rv_dir(username) -> str:
    base_dir = "/user/signoff.dsa/DASHCACHE"
    user_rv_dir = os.path.join(base_dir, f"SOL_{username}")
    appcache_dir = os.path.join(user_rv_dir, f"cache")
    log_dir = os.path.join(user_rv_dir, f"log")
    os.makedirs(user_rv_dir, mode=stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO, exist_ok=True)
    os.makedirs(log_dir, mode=stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO, exist_ok=True)
    os.makedirs(appcache_dir, mode=stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO, exist_ok=True)
    return user_rv_dir, log_dir, appcache_dir


USERNAME = os.getenv("USER")

USER_DIR, LOG_DIR, APPCACHE_DIR = get_user_rv_dir(USERNAME)

SETTINGS_FILE = os.path.join(USER_DIR, "settings")
DEFAULT_WORKSPACE_DIR = os.path.join(USER_DIR, "WORKSPACE")

ENABLE_MONITORING = True
custom_yaml_path = os.path.join(USER_DIR, "custom_signoff_applications.yaml")
default_yaml_path = os.path.join(USER_DIR, "signoff_applications.yaml")
shutil.copy2("/user/signoff.dsa/launcher/signoff_applications.yaml", default_yaml_path)
SIGNOFF_APPLICATION_YAML = custom_yaml_path if os.path.exists(custom_yaml_path) else default_yaml_path

RUN_SCRIPTS = "/user/signoff.dsa/launcher/RUNSCRIPTS"
```

## File: utils/sol_constants.py
```python
IDENTIFIER = "+"
```

## File: utils/update_config.py
```python
#!/user/signoff.dev/deepwonwoo/SW/miniconda3/envs/viewer/bin/python
import sys
import os
import pwd
import yaml
import argparse
import requests

from datetime import datetime

USERNAME = os.getenv("USER", "unknown")
DEVWORKS_URL = "http://dsky2527:7089"
SYSTEM_ID = "sorv"
SYSTEM_PASS = "Lg=="


def get_auth_token():

    url = f"{DEVWORKS_URL}/send/system/authentication"
    payload = {"systemId": SYSTEM_ID, "systemPass": SYSTEM_PASS}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        raise Exception("Failed to get authentication token")


def send_devworks_message(params):
    try:
        token = get_auth_token()
        url = f"{DEVWORKS_URL}/api/send"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "params": params,  # %s님의 %s 이(가) %s 되었습니다.( %s )
            "sender": pwd.getpwnam(USERNAME).pw_uid,
            "recipients": [pwd.getpwnam(USERNAME).pw_uid],
            "purpose": "Signoff Launcher Operation",
            "project": "Launcher",
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Devworks message sending failed: {e}")


def is_launcher_environment():
    config_path = os.path.join(os.path.dirname(os.getcwd()), "job_config.yaml")
    return os.path.exists(config_path)


def update_config(config_path, status=None, message=None, job_id=None):

    if not is_launcher_environment():
        # if is not from Launcher
        if status:
            print(f"Status: {status}")
        if message:
            print(f"Message: {message}")
        if job_id:
            print(f"Job ID: {job_id}")
        return True

    """    Update job_config.yaml with given updates    """
    try:
        # Read current config
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        if status:
            config["status"] = status
            # status 변경 시 자동으로 시간 기록
            if status == "running":
                config["job_start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_devworks_message([USERNAME, f"{config['app']} 작업", "시작", config["workspace"]])

            elif status == "done":
                config["job_finish_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_devworks_message([USERNAME, f"{config['app']} 작업", "완료", config["workspace"]])

            elif status == "failed":
                config["job_finish_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_devworks_message([USERNAME, f"{config['app']} 작업", "실패", config["workspace"]])

            elif status == "stop":
                config["job_finish_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_devworks_message([USERNAME, f"{config['app']} 작업", "중지", config["workspace"]])

        if message is not None:
            config["message"] = message
        if job_id is not None:
            config["job_id"] = job_id

        with open(config_path, "w") as f:
            yaml.dump(config, f)

    except Exception as e:
        print(f"Error updating config: {e}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Update fields in job_config.yaml")
    parser.add_argument("--config", help="Path to job_config.yaml", default="../job_config.yaml")
    status_group = parser.add_mutually_exclusive_group()
    status_group.add_argument("--start", action="store_true", help="Set status as running (for job start)")
    status_group.add_argument("--fail", action="store_true", help="Set status as failed (for job failure)")
    status_group.add_argument("--done", action="store_true", help="Set status as done (for job completion)")
    status_group.add_argument("--stop", action="store_true", help="Set status as stop (for job stop)")

    parser.add_argument("--msg", help="Update status message")
    parser.add_argument("--jobID", type=int, help="Update LSF job ID", default=None)
    parser.add_argument("--devworks", type=str, nargs="+", help="Send devworks message")  # 한 개 이상의 값을 리스트로 처리
    args = parser.parse_args()
    # 상태값 결정
    status = None
    if args.start:
        status = "running"
    elif args.fail:
        status = "failed"
    elif args.done:
        status = "done"
    elif args.stop:
        status = "stop"

    if not os.path.exists(args.config):  # not from launcher
        print("not from launcher")
        if status:
            print(f"Status: {status}")
        if args.msg:
            print(f"Message: {args.msg}")
        sys.exit()

    success = update_config(args.config, status, args.msg, args.jobID)

    if args.devworks and len(args.devworks) == 2:
        send_devworks_message([USERNAME] + args.devworks + [os.getcwd()])  # %s님의 %s 이(가) %s 되었습니다.( %s )


if __name__ == "__main__":
    main()
```

## File: utils/workspace.py
```python
import os
import glob
import json
from dash import ctx
from pathlib import Path
import dash_mantine_components as dmc
import dash_blueprint_components as dbpc
from dash import Input, Output, State, html, no_update, exceptions, dcc
from utils.settings import SETTINGS_FILE, DEFAULT_WORKSPACE_DIR
from utils.logger import logger
from datetime import datetime


def get_workspace_dir():
    """Get current workspace directory"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                workspace_dir = settings.get("WORKSPACE_DIR", DEFAULT_WORKSPACE_DIR)
                return workspace_dir
    except Exception:
        set_workspace_dir(DEFAULT_WORKSPACE_DIR)
    return os.path.abspath(DEFAULT_WORKSPACE_DIR)


def get_workspace_history():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                history = settings.get("HISTORY_WORKSPACE_DIRS", [])
                logger.debug(f"getting history workspace directory from settings: {history}")
                return history
    except Exception as e:
        logger.error(f"Error loading workspace history: {str(e)}")
        return []

    return []


def set_workspace_dir(path):
    logger.debug(f"Setting workspace directory to {path}")
    try:
        path = os.path.expanduser(path)
        path = os.path.abspath(path)

        # Create directory if it doesn't exist
        Path(path).mkdir(parents=True, exist_ok=True)

        # 현재 설정 파일 읽기
        current_settings = {}
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                try:
                    current_settings = json.load(f)
                except json.JSONDecodeError:
                    current_settings = {}

        # 현재 시간 정보
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 히스토리 업데이트
        history = current_settings.get("HISTORY_WORKSPACE_DIRS", [])

        # 같은 경로가 이미 있는지 확인
        existing_entry_index = None
        for i, entry in enumerate(history):
            if entry.get("path") == path:
                existing_entry_index = i
                break

        # 새 항목 생성
        new_entry = {"path": path, "last_used": current_time}

        # 기존 항목이 있으면 제거 (나중에 맨 앞에 추가)
        if existing_entry_index is not None:
            history.pop(existing_entry_index)

        # 새 항목을 맨 앞에 추가 (최신순 정렬)
        history.insert(0, new_entry)

        # 최대 10개로 제한
        history = history[:10]

        # 설정 업데이트
        current_settings["WORKSPACE_DIR"] = path
        current_settings["HISTORY_WORKSPACE_DIRS"] = history

        # 설정 파일 저장
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(current_settings, f, indent=2)
        return True

    except Exception as e:
        logger.error(f"Error setting workspace directory: {str(e)}", exc_info=True)
        return False


def remove_from_workspace_history(path):
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)

            history = settings.get("HISTORY_WORKSPACE_DIRS", [])
            # 경로가 일치하는 항목 제거
            settings["HISTORY_WORKSPACE_DIRS"] = [entry for entry in history if entry.get("path") != path]

            # 현재 사용 중인 경로와 일치하면 남은 첫 번째 항목으로 변경
            if settings.get("WORKSPACE_DIR") == path and settings["HISTORY_WORKSPACE_DIRS"]:
                settings["WORKSPACE_DIR"] = settings["HISTORY_WORKSPACE_DIRS"][0]["path"]

            # 설정 파일 저장
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

            return True

    except Exception as e:
        logger.error(f"Error removing workspace from history: {str(e)}")
        return False

    return False


def get_job_count():
    """Get total number of jobs in current workspace"""
    try:
        workspace_dir = get_workspace_dir()
        if not os.path.exists(workspace_dir):
            return 0

        # job 디렉토리 카운트
        # job_config.yaml이 있는 디렉토리만 유효한 job으로 간주
        job_count = sum(
            1 for item in os.listdir(workspace_dir) if os.path.isdir(os.path.join(workspace_dir, item)) and os.path.exists(os.path.join(workspace_dir, item, "job_config.yaml"))
        )

        return job_count

    except Exception as e:
        logger.error(f"Error counting jobs: {str(e)}")
        return 0


class WorkspaceDrawer:
    def __init__(self, app):
        self.app = app
        self.register_callbacks(app)

    def _get_directory_contents(self, path):
        """Get formatted directory contents with restrictions"""
        try:
            contents = []
            max_items = 100  # 최대 표시 항목 수 제한
            item_count = 0
            with os.scandir(path) as it:
                for entry in it:
                    # 1. 최대 항목 수 체크
                    if item_count >= max_items:
                        contents.append(
                            dbpc.Card(
                                dbpc.EntityTitle(
                                    title=f"... (Showing {max_items} of many items)",
                                    heading="Text",
                                    icon="warning-sign",
                                )
                            )
                        )
                        break
                    try:
                        # 2. 파일/디렉토리 소유자 확인
                        stat_info = entry.stat()
                        # pwd.getpwuid를 사용하면 더 정확하지만, 성능상의 이유로 생략
                        # 3. 현재 사용자 소유 파일/디렉토리만 표시

                        if os.getuid() == stat_info.st_uid:
                            icon = "folder-open" if entry.is_dir() else "document"
                            contents.append(
                                dbpc.Card(
                                    dbpc.EntityTitle(
                                        title=entry.name,
                                        heading="Text",
                                        icon=icon,
                                        ellipsize=True,
                                    )
                                )
                            )
                            item_count += 1
                    except (PermissionError, OSError):
                        # 권한 문제 등은 무시하고 계속 진행
                        continue
                return (
                    dbpc.CardList(contents)
                    if contents
                    else [
                        dmc.Text(
                            "(Empty directory or no accessible items)",
                            size="sm",
                            c="dimmed",
                        )
                    ]
                )

        except PermissionError:
            return [
                dmc.Text(
                    "Permission denied: You don't have access to this directory",
                    c="red",
                )
            ]
        except Exception as e:
            return [dmc.Text(f"Error reading directory: {str(e)}", c="red")]

    def _get_size(self, path):
        """재귀적으로 디렉토리/파일 크기 계산"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            total = 0
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total += os.path.getsize(fp)
            return total

    def _format_size(self, size):
        """바이트 크기를 사람이 읽기 쉬운 형태로 변환"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def validate_workspace_path(self, path):
        """
        Validate workspace path without creating it
        Returns: (is_valid, message, status)
        """
        if not path:
            return False, "Workspace path is required", "error"

        try:
            path = os.path.expanduser(path)
            path = os.path.abspath(path)

            if os.path.exists(path):
                if not os.path.isdir(path):
                    return False, "Path exists but is not a directory", "error"

                if not os.access(path, os.W_OK):
                    return False, "Directory exists but is not writable", "error"

                return True, "Valid workspace directory", "success"

            # Path doesn't exist - check if parent is writable
            parent = os.path.dirname(path)
            if not os.access(parent, os.W_OK):
                return (
                    False,
                    f"Cannot create directory in {parent} - permission denied",
                    "error",
                )

            return True, "Directory will be created when applied", "warning"

        except Exception as e:
            return False, f"Invalid path: {str(e)}", "error"

    def layout(self):
        return dbpc.Drawer(
            id="workspace-drawer",
            title=get_workspace_dir(),
            icon="project",
            isOpen=False,
            position="right",
            children=[
                html.Div(
                    children=[
                        dmc.Card(
                            children=[
                                dmc.Group(
                                    [
                                        dmc.Text("Workspace Settings", size="lg", w=500),
                                        dbpc.Tooltip(
                                            content="Default directory where job workspaces will be created",
                                            children=dbpc.Button(icon="help", small=12),
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                                dmc.Space(h="md"),
                                dmc.Group(
                                    [
                                        dbpc.InputGroup(
                                            id="workspace-path",
                                            placeholder="/path/to/workspace",
                                            leftElement=dbpc.Button(icon="projects", small=True),
                                            rightElement=dbpc.Button(
                                                "Apply Changes",
                                                id="apply-workspace-btn",
                                                intent="primary",
                                                icon="exchange",
                                            ),
                                            value=get_workspace_dir(),
                                            style={"width": "100%"},
                                        )
                                    ],
                                    grow=True,
                                ),
                                dmc.Text(
                                    id="workspace-status",
                                    size="sm",
                                    style={"marginTop": 10},
                                ),
                                dmc.Space(h="md"),
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            "Current workspace contents:",
                                            size="sm",
                                            w=500,
                                        ),
                                        dbpc.Button(
                                            id="refresh-workspace",
                                            icon="refresh",
                                            minimal=True,
                                            small=True,
                                        ),
                                    ],
                                    justify="space-between",
                                ),
                                html.Div(
                                    id="workspace-contents",
                                    style={
                                        "marginTop": 10,
                                        "maxHeight": "200px",
                                        "overflow": "auto",
                                        "padding": "10px",
                                        "border": f"1px solid {dmc.DEFAULT_THEME['colors']['gray'][3]}",
                                        "borderRadius": "4px",
                                    },
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            p="md",
                        )
                    ],
                    className="bp5-drawer-body",
                    style={"margin": "15px"},
                ),
            ],
        )

    def workspace_setup_modal(self):
        """Stepper 컴포넌트를 사용한 워크스페이스 설정 모달"""
        return dmc.Modal(
            id="workspace-setup-modal",
            opened=True,
            title=dmc.Title("Workspace Setup", order=3, mb="xs"),
            closeOnClickOutside=False,
            closeOnEscape=False,
            size="xl",
            styles={"modal": {"width": "1000px", "maxWidth": "95vw"}},
            children=[
                dmc.Paper(
                    children=[
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        dbpc.Icon(icon="info-sign", size=16, color="blue"),
                                        dmc.Text("표준화된 워크스페이스 경로를 설정해주세요.", size="xs"),
                                    ],
                                    justify="flex-start",
                                ),
                                dmc.Badge(
                                    "/{STORAGE}/SIGNOFF/{LIBRARY}/{CELL}/{USER}",
                                    color="blue",
                                    size="lg",
                                    variant="outline",
                                    radius="xs",
                                ),
                            ],
                            gap="xs",
                        ),
                    ],
                    p="md",
                    withBorder=True,
                    shadow="xs",
                    style={"backgroundColor": "rgba(173, 216, 230, 0.1)"},
                    mb="md",
                ),
                # 진행 경로 표시 - 개선된 시각화
                dmc.Paper(
                    children=[
                        dmc.Group(
                            [
                                dmc.Text("설정 중인 경로:", size="sm", c="dimmed"),
                                dmc.Group(
                                    [
                                        dmc.Badge(id="current-storage-badge", color="blue", variant="filled", size="sm", children="", style={"display": "none"}),
                                        dmc.Text("/SIGNOFF/", size="sm", fw=500),
                                        dmc.Badge(id="current-library-badge", color="indigo", variant="filled", size="sm", children="", style={"display": "none"}),
                                        dmc.Text("/", size="sm", fw=500, id="library-separator", style={"display": "none"}),
                                        dmc.Badge(id="current-cell-badge", color="violet", variant="filled", size="sm", children="", style={"display": "none"}),
                                        dmc.Text("/", size="sm", fw=500, id="cell-separator", style={"display": "none"}),
                                        dmc.Badge(
                                            id="current-user-badge", color="green", variant="filled", size="sm", children=os.getenv("USER", "unknown"), style={"display": "none"}
                                        ),
                                    ],
                                    gap="xs",
                                ),
                            ],
                            justify="evenly",
                        ),
                    ],
                    p="sm",
                    withBorder=True,
                    mb="md",
                ),
                # Stepper 컴포넌트
                dmc.Stepper(
                    id="workspace-stepper",
                    active=0,
                    size="sm",
                    styles={"root": {"width": "100%"}},  # 스텝퍼 너비 조정
                    children=[
                        # 1단계: MOUNTED_STORAGE 선택
                        dmc.StepperStep(
                            label="Storage 선택",
                            description="마운트된 스토리지를 선택하세요",
                            children=dmc.Stack(
                                [
                                    dmc.Select(
                                        id="mounted-storage-select",
                                        label="스토리지 경로",
                                        placeholder="스토리지를 선택하세요",
                                        data=[],  # 여기에 마운트된 스토리지 목록이 동적으로 채워짐
                                        searchable=True,
                                        required=True,
                                        mt="md",
                                        styles={"root": {"width": "100%"}},
                                    ),
                                    dmc.Paper(
                                        id="storage-permission-box",
                                        style={"display": "none"},
                                        p="sm",
                                        withBorder=True,
                                        mt="xs",
                                        children=[
                                            dmc.Group(
                                                [
                                                    dbpc.Icon(icon="None", id="storage-permission-icon", size=16),
                                                    dmc.Text(id="storage-permission-status", size="sm"),
                                                ],
                                                gap="xs",
                                            ),
                                        ],
                                    ),
                                ],
                                gap="xs",
                            ),
                        ),
                        # 2단계: LIBRARY_NAME 및 CELL_NAME 선택 - 개선된 버전
                        dmc.StepperStep(
                            label="Library 및 Cell 선택",
                            description="Library와 Cell을 선택하세요",
                            children=dmc.Stack(
                                [
                                    # 라이브러리 선택 섹션
                                    dmc.Title("Library 선택", order=5, mb="xs"),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                [
                                                    dmc.Select(
                                                        id="library-name-select",
                                                        label="기존 Library",
                                                        placeholder="Library를 선택하세요",
                                                        data=[],
                                                        searchable=True,
                                                        clearable=True,
                                                        style={"width": "100%"},
                                                    ),
                                                    dmc.Button(
                                                        "새 Library 생성",
                                                        id="create-new-library-btn",
                                                        variant="light",
                                                        size="xs",
                                                        leftSection=dbpc.Icon(icon="plus", size=12),
                                                        style={"alignSelf": "flex-start", "marginTop": "5px"},
                                                    ),
                                                ],
                                                style={"width": "48%"},
                                            ),
                                            dmc.Stack(
                                                [
                                                    dmc.TextInput(
                                                        id="new-library-input",
                                                        label="새 Library 이름",
                                                        placeholder="새 Library 이름 입력",
                                                        disabled=True,
                                                        style={"width": "100%"},
                                                    ),
                                                    dmc.Group(
                                                        [
                                                            dmc.Button(
                                                                "생성",
                                                                id="confirm-new-library-btn",
                                                                color="green",
                                                                size="xs",
                                                                disabled=True,
                                                            ),
                                                            dmc.Button(
                                                                "취소",
                                                                id="cancel-new-library-btn",
                                                                color="gray",
                                                                size="xs",
                                                                variant="outline",
                                                                disabled=True,
                                                            ),
                                                        ],
                                                        style={"alignSelf": "flex-start", "marginTop": "5px"},
                                                    ),
                                                ],
                                                style={"width": "48%"},
                                            ),
                                        ],
                                        justify="apart",
                                        grow=True,
                                    ),
                                    dmc.Paper(
                                        id="library-permission-box",
                                        style={"display": "none"},
                                        p="sm",
                                        withBorder=True,
                                        mt="xs",
                                        mb="md",
                                        children=[
                                            dmc.Group(
                                                [
                                                    dbpc.Icon(icon="None", id="library-permission-icon", size=16),
                                                    dmc.Text(id="library-permission-status", size="sm"),
                                                ],
                                                gap="xs",
                                            ),
                                        ],
                                    ),
                                    # 셀 선택 섹션 - 라이브러리 선택이 완료되면 활성화됨
                                    dmc.Divider(labelPosition="center", label="Cell 설정", mt="md", mb="md"),
                                    dmc.Group(
                                        [
                                            dmc.Stack(
                                                [
                                                    dmc.Select(
                                                        id="cell-name-select",
                                                        label="기존 Cell",
                                                        placeholder="Cell을 선택하세요",
                                                        data=[],
                                                        searchable=True,
                                                        clearable=True,
                                                        disabled=True,  # 라이브러리가 선택되기 전에는 비활성화
                                                        style={"width": "100%"},
                                                    ),
                                                    dmc.Button(
                                                        "새 Cell 생성",
                                                        id="create-new-cell-btn",
                                                        variant="light",
                                                        size="xs",
                                                        leftSection=dbpc.Icon(icon="plus", size=12),
                                                        disabled=True,  # 라이브러리가 선택되기 전에는 비활성화
                                                        style={"alignSelf": "flex-start", "marginTop": "5px"},
                                                    ),
                                                ],
                                                style={"width": "48%"},
                                            ),
                                            dmc.Stack(
                                                [
                                                    dmc.TextInput(
                                                        id="new-cell-input",
                                                        label="새 Cell 이름",
                                                        placeholder="새 Cell 이름 입력",
                                                        disabled=True,
                                                        style={"width": "100%"},
                                                    ),
                                                    dmc.Group(
                                                        [
                                                            dmc.Button(
                                                                "생성",
                                                                id="confirm-new-cell-btn",
                                                                color="green",
                                                                size="xs",
                                                                disabled=True,
                                                            ),
                                                            dmc.Button(
                                                                "취소",
                                                                id="cancel-new-cell-btn",
                                                                color="gray",
                                                                size="xs",
                                                                variant="outline",
                                                                disabled=True,
                                                            ),
                                                        ],
                                                        style={"alignSelf": "flex-start", "marginTop": "5px"},
                                                    ),
                                                ],
                                                style={"width": "48%"},
                                            ),
                                        ],
                                        justify="apart",
                                        grow=True,
                                    ),
                                    dmc.Paper(
                                        id="cell-permission-box",
                                        style={"display": "none"},
                                        p="sm",
                                        withBorder=True,
                                        mt="xs",
                                        children=[
                                            dmc.Group(
                                                [
                                                    dbpc.Icon(icon="None", id="cell-permission-icon", size=16),
                                                    dmc.Text(id="cell-permission-status", size="sm"),
                                                ],
                                                gap="xs",
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                        ),
                        dmc.StepperStep(
                            label="설정 완료",
                            description="워크스페이스 경로 확인",
                            children=dmc.Stack(
                                [
                                    dmc.Alert(
                                        id="final-path-alert",
                                        title="아래 경로로 워크스페이스가 설정됩니다",
                                        color="blue",
                                        icon=dbpc.Icon(icon="info-sign"),
                                    ),
                                    dmc.Paper(
                                        p="md",
                                        withBorder=True,
                                        shadow="sm",
                                        style={"backgroundColor": "rgba(0, 0, 0, 0.03)"},
                                        children=[
                                            dmc.Group(
                                                [
                                                    dbpc.Icon(icon="folder", size=18),
                                                    dmc.Text(id="final-workspace-path", fw=500),
                                                ]
                                            ),
                                        ],
                                    ),
                                    dmc.Text("이 경로가 없는 경우 자동으로 생성됩니다. 경로에 대한 적절한 권한이 있는지 확인하세요.", mt="md", size="sm", c="dimmed"),
                                    # RUNSCRIPT 폴더 체크 결과 표시 영역 추가
                                    dmc.Paper(
                                        id="runscript-check-box",
                                        style={"display": "none"},
                                        p="sm",
                                        withBorder=True,
                                        mt="md",
                                        children=[
                                            dmc.Group(
                                                [
                                                    dbpc.Icon(icon="None", id="runscript-check-icon", size=16),
                                                    dmc.Text(id="runscript-check-status", size="sm"),
                                                ],
                                                gap="xs",
                                            ),
                                        ],
                                    ),
                                ],
                                gap="md",
                            ),
                        ),
                    ],
                ),
                # 탐색 버튼
                dmc.Group(
                    [
                        dmc.Button(
                            "이전",
                            id="stepper-prev-button",
                            variant="outline",
                            disabled=True,
                        ),
                        dmc.Button(
                            "다음",
                            id="stepper-next-button",
                        ),
                    ],
                    justify="flex-end",
                    mt="xl",
                    mb="md",
                ),
                # 사용자 정의 경로 토글 버튼
                dmc.Group(
                    [
                        dmc.Button(
                            "사용자 정의 경로 사용",
                            id="toggle-custom-path-button",
                            variant="subtle",
                            rightSection=dbpc.Icon(icon="caret-down", size=12),
                            color="gray",
                        ),
                    ],
                    justify="center",
                    mt="sm",
                ),
                # 사용자 정의 경로 영역
                dmc.Collapse(
                    id="custom-path-collapse",
                    opened=False,
                    children=[
                        dmc.Paper(
                            children=[
                                dmc.Divider(labelPosition="center", label="사용자 정의 경로 설정", mt="sm", mb="md"),
                                dmc.TextInput(
                                    id="custom-workspace-path",
                                    label="사용자 정의 워크스페이스 경로",
                                    placeholder="예: /path/to/your/custom/workspace",
                                    leftSection=dbpc.Icon(icon="folder-open", size=16),
                                    required=True,
                                    styles={"root": {"width": "100%"}},
                                ),
                                dmc.Paper(
                                    id="custom-path-permission-box",
                                    style={"display": "none"},
                                    p="sm",
                                    withBorder=True,
                                    mt="xs",
                                    children=[
                                        dmc.Group(
                                            [
                                                dbpc.Icon(icon="None", id="custom-path-permission-icon", size=16),
                                                dmc.Text(id="custom-path-status", size="sm"),
                                            ],
                                            gap="xs",
                                        ),
                                    ],
                                ),
                                dmc.Button(
                                    "이 경로로 설정",
                                    id="apply-custom-path-btn",
                                    mt="md",
                                    variant="light",
                                    fullWidth=True,
                                    disabled=True,  # 기본적으로 비활성화, 유효한 경로가 입력되면 활성화
                                ),
                            ],
                            p="md",
                            withBorder=True,
                            shadow="xs",
                            mt="md",
                        ),
                    ],
                ),
                # 알림 영역
                dmc.Alert(
                    id="workspace-stepper-alert",
                    title="",
                    color="red",
                    icon=dbpc.Icon(icon="warning-sign"),
                    style={"display": "none"},
                    mt="md",
                ),
                # 데이터 저장용 Store
                dcc.Store(id="workspace-stepper-data", data={}),
                dcc.Store(id="workspace-path-parts", data={"storage": "", "library": "", "cell": "", "user": os.getenv("USER", "unknown")}),
            ],
        )

    def register_callbacks(self, app):
        # self.register_workspace_setup_modal_callbacks(app)

        @app.callback(
            Output("workspace-drawer", "isOpen"),
            Input("workspace-btn", "n_clicks"),
            prevent_initial_call=True,
        )
        def open_setting_drawer(n_clicks):
            return n_clicks is not None

        @app.callback(
            Output("workspace-drawer", "isOpen", allow_duplicate=True),
            Input("close-settings", "n_clicks"),
            prevent_initial_call=True,
        )
        def close_settings(_):
            return False

        @app.callback(
            [
                Output("workspace-path", "intent"),
                Output("workspace-status", "children"),
                Output("workspace-status", "color"),
                Output("workspace-contents", "children"),
                Output("apply-workspace-btn", "disabled"),
            ],
            [Input("workspace-path", "value"), Input("refresh-workspace", "n_clicks")],
            prevent_initial_call=True,
        )
        def validate_workspace(path, _):
            """Validate workspace path and update UI accordingly"""
            if not path:
                return "warning", "Workspace path is required", "red", [], True

            is_valid, message, status = self.validate_workspace_path(path)

            # 경로가 존재하는 경우에만 contents 표시
            contents = []
            if os.path.isdir(path):
                try:
                    contents = self._get_directory_contents(path)
                except Exception as e:
                    contents = [dmc.Text(f"Error reading directory: {str(e)}", c="red")]
            else:
                contents = [dmc.Text("Directory will be created when applied", size="sm", c="dimmed")]

            return (
                "success" if is_valid else "warning",
                message,
                {"success": "green", "warning": "orange", "error": "red"}[status],
                contents,
                not is_valid,  # apply 버튼은 유효한 경로일 때만 활성화
            )

        @app.callback(
            Output("workspace-path", "value"),
            Output("workspace-status", "children", allow_duplicate=True),
            Output("workspace-status", "color", allow_duplicate=True),
            Output("workspace-display-indicator", "children", allow_duplicate=True),
            Output("workspace-drawer", "title", allow_duplicate=True),
            Output("workspace-display-indicator", "label", allow_duplicate=True),
            Input("apply-workspace-btn", "n_clicks"),
            State("workspace-path", "value"),
            prevent_initial_call=True,
        )
        def update_workspace(_, path):
            """Handle workspace directory creation/update when Apply is clicked"""
            if not path:
                raise exceptions.PreventUpdate
            try:
                # First validate the path
                is_valid, message, status = self.validate_workspace_path(path)
                if not is_valid:
                    return no_update, message, "red", no_update, no_update, no_update

                # Create directory if it doesn't exist
                path = os.path.abspath(os.path.expanduser(path))
                if not os.path.exists(path):
                    try:
                        os.makedirs(path)
                        os.chmod(path, 0o755)
                    except Exception as e:
                        return (
                            no_update,
                            f"Failed to create directory: {str(e)}",
                            "red",
                            no_update,
                            no_update,
                            no_update,
                        )

                # Update settings file
                if set_workspace_dir(path):
                    global WORKSPACE_DIR
                    WORKSPACE_DIR = path
                    return (
                        path,
                        "Workspace updated successfully",
                        "green",
                        path,
                        path,
                        str(get_job_count()),
                    )

                return (
                    no_update,
                    "Failed to save workspace settings",
                    "red",
                    no_update,
                    no_update,
                    no_update,
                )

            except Exception as e:
                return no_update, f"Error updating workspace: {str(e)}", "red", no_update, no_update, no_update

        @app.callback(
            Output("workspace-history-select", "data"),
            Input("workspace-drawer", "isOpen"),
            prevent_initial_call=True,
        )
        def load_workspace_history(is_open):
            if not is_open:
                raise exceptions.PreventUpdate

            history = get_workspace_history()
            if not history:
                return []

            # 드롭다운용 데이터 형태로 변환
            dropdown_data = []
            for entry in history:
                path = entry.get("path", "")
                last_used = entry.get("last_used", "")
                if path:
                    dropdown_data.append({"value": path, "label": f"{path}", "description": f"Last used: {last_used}"})
            return dropdown_data

            # 히스토리에서 워크스페이스 선택 시 경로 설정

        @app.callback(
            Output("workspace-path", "value", allow_duplicate=True),
            Input("workspace-history-select", "value"),
            prevent_initial_call=True,
        )
        def select_workspace_from_history(selected_path):
            if not selected_path:
                raise exceptions.PreventUpdate
            return selected_path

        # 히스토리 선택 시 삭제 버튼 활성화
        @app.callback(
            Output("remove-workspace-history", "disabled"),
            Input("workspace-history-select", "value"),
        )
        def toggle_remove_button(selected_path):
            return selected_path is None

        # 히스토리에서 선택한 워크스페이스 삭제
        @app.callback(
            Output("workspace-history-select", "value", allow_duplicate=True),
            Output("workspace-history-select", "data", allow_duplicate=True),
            Input("remove-workspace-history", "n_clicks"),
            State("workspace-history-select", "value"),
            prevent_initial_call=True,
        )
        def remove_workspace_history_entry(n_clicks, selected_path):
            if not n_clicks or not selected_path:
                raise exceptions.PreventUpdate

            # 히스토리에서 삭제
            success = remove_from_workspace_history(selected_path)

            if success:
                # 삭제 후 업데이트된 히스토리 다시 로드
                history = get_workspace_history()
                dropdown_data = []
                for entry in history:
                    path = entry.get("path", "")
                    last_used = entry.get("last_used", "")
                    if path:
                        dropdown_data.append({"value": path, "label": f"{path}", "description": f"Last used: {last_used}"})

                # 선택값 초기화 및 새 데이터로 드롭다운 업데이트
                return None, dropdown_data

            raise exceptions.PreventUpdate

    def register_workspace_setup_modal_callbacks(self, app):

        # 마운트된 스토리지 목록 로드
        @app.callback(
            Output("mounted-storage-select", "data"),
            Input("workspace-setup-modal", "opened"),
        )
        def load_mounted_storages(opened):
            if not opened:
                raise exceptions.PreventUpdate

            try:
                # 테스트 환경을 위한 기본값 추가
                storages = [
                    {"value": "C:\\Users\\deepw\\OneDrive\\문서", "label": "문서"},
                    {"value": "C:\\Users\\deepw\\OneDrive\\문서\\Python", "label": "python"},
                    {"value": "C:\\Users\\deepw\\OneDrive\\문서\\Knox Meeting", "label": "Knox Meeting"},
                ]
                return storages
                # 실제 환경에서는 시스템 명령어 또는 glob를 사용하여 마운트된 스토리지 목록을 가져옴
                # 예: glob.glob('/*')
                import glob

                storages = []

                # 마운트된 스토리지 목록 가져오기
                mount_paths = glob.glob("/*")
                for path in mount_paths:
                    if os.path.isdir(path) and os.access(path, os.R_OK):
                        label = os.path.basename(path)
                        storages.append({"value": path, "label": label})
                return storages
            except Exception as e:
                logger.error(f"스토리지 목록 로드 중 오류: {str(e)}")
                return [{"value": "/", "label": "Root"}]

        # 스토리지 선택 시 권한 확인 및 배지 표시
        @app.callback(
            [
                Output("storage-permission-status", "children"),
                Output("storage-permission-icon", "icon"),
                Output("storage-permission-icon", "color"),
                Output("storage-permission-box", "style"),
                Output("current-storage-badge", "children"),
                Output("current-storage-badge", "style"),
                Output("workspace-path-parts", "data"),
                Output("stepper-next-button", "disabled", allow_duplicate=True),
            ],
            Input("mounted-storage-select", "value"),
            prevent_initial_call=True,
        )
        def check_storage_permission(storage_path):
            if not storage_path:
                return ("", "", "", {"display": "none"}, "", {"display": "none"}, {"storage": "", "library": "", "cell": "", "user": os.getenv("USER", "unknown")}, True)
            # 경로 구성
            signoff_path = os.path.join(storage_path, "SIGNOFF")

            # 권한 체크
            try:
                if os.path.exists(signoff_path):
                    if os.access(signoff_path, os.W_OK):
                        return (
                            f"{signoff_path} 경로에 쓰기 권한이 있습니다.",
                            "tick-circle",
                            "green",
                            {"display": "block"},
                            os.path.basename(storage_path),
                            {"display": "inline-flex"},
                            {"storage": storage_path, "library": "", "cell": "", "user": os.getenv("USER", "unknown")},
                            False,
                        )
                    else:
                        return (
                            f"{signoff_path} 경로에 쓰기 권한이 없습니다.",
                            "warning-sign",
                            "orange",  # 경고만 표시, 진행은 허용
                            {"display": "block"},
                            os.path.basename(storage_path),
                            {"display": "inline-flex"},
                            {"storage": storage_path, "library": "", "cell": "", "user": os.getenv("USER", "unknown")},
                            False,
                        )
                else:
                    if os.access(storage_path, os.W_OK):
                        return (
                            f"{signoff_path} 경로가 없습니다. 새로 생성할 수 있습니다.",
                            "info-sign",
                            "blue",
                            {"display": "block"},
                            os.path.basename(storage_path),
                            {"display": "inline-flex"},
                            {"storage": storage_path, "library": "", "cell": "", "user": os.getenv("USER", "unknown")},
                            False,
                        )
                    else:
                        return (
                            f"{storage_path} 경로에 쓰기 권한이 없어 SIGNOFF 디렉토리를 생성할 수 없습니다.",
                            "warning-sign",
                            "orange",  # 경고만 표시, 진행은 허용
                            {"display": "block"},
                            os.path.basename(storage_path),
                            {"display": "inline-flex"},
                            {"storage": storage_path, "library": "", "cell": "", "user": os.getenv("USER", "unknown")},
                            False,
                        )
            except Exception as e:
                return (
                    f"권한 확인 중 오류 발생: {str(e)}",
                    "error",
                    "red",
                    {"display": "block"},
                    os.path.basename(storage_path) if storage_path else "",
                    {"display": "inline-flex"},
                    {"storage": storage_path, "library": "", "cell": "", "user": os.getenv("USER", "unknown")},
                    True,
                )

        # 스토리지 선택 시 라이브러리 목록 로드
        @app.callback(
            Output("library-name-select", "data"),
            Input("mounted-storage-select", "value"),
            prevent_initial_call=True,
        )
        def load_libraries(storage_path):
            if not storage_path:
                raise exceptions.PreventUpdate

            signoff_path = os.path.join(storage_path, "SIGNOFF")
            libraries = []

            try:
                if os.path.exists(signoff_path) and os.path.isdir(signoff_path):
                    # SIGNOFF 디렉토리 내의 라이브러리 목록 가져오기
                    for item in os.listdir(signoff_path):
                        lib_path = os.path.join(signoff_path, item)
                        if os.path.isdir(lib_path):
                            libraries.append({"value": item, "label": item})

                return libraries
            except Exception as e:
                logger.error(f"라이브러리 목록 로드 중 오류: {str(e)}")
                return []

        # 라이브러리 선택 또는 입력 시 권한 체크 및 셀 목록 로드
        @app.callback(
            [
                Output("library-permission-status", "children", allow_duplicate=True),
                Output("library-permission-icon", "icon", allow_duplicate=True),
                Output("library-permission-icon", "color", allow_duplicate=True),
                Output("library-permission-box", "style", allow_duplicate=True),
                Output("current-library-badge", "children", allow_duplicate=True),
                Output("current-library-badge", "style", allow_duplicate=True),
                Output("library-separator", "style", allow_duplicate=True),
                Output("cell-name-select", "data", allow_duplicate=True),
            ],
            [
                Input("library-name-select", "value"),
                Input("new-library-input", "value"),
            ],
            [
                State("mounted-storage-select", "value"),
                State("workspace-path-parts", "data"),
            ],
            prevent_initial_call=True,
        )
        def handle_library_selection(selected_lib, new_lib, storage_path, path_parts):
            triggered_id = ctx.triggered_id

            if not storage_path:
                raise exceptions.PreventUpdate

            # 선택 또는 입력된 라이브러리 이름 결정
            library_name = selected_lib if selected_lib else new_lib
            if not library_name:
                return ("", "", "", {"display": "none"}, "", {"display": "none"}, {"display": "none"}, [])

            # 경로 구성
            signoff_path = os.path.join(storage_path, "SIGNOFF")
            library_path = os.path.join(signoff_path, library_name)

            # 셀 목록 로드
            cells = []
            try:
                if os.path.exists(library_path) and os.path.isdir(library_path):
                    for item in os.listdir(library_path):
                        cell_path = os.path.join(library_path, item)
                        if os.path.isdir(cell_path):
                            cells.append({"value": item, "label": item})
            except Exception as e:
                logger.error(f"셀 목록 로드 중 오류: {str(e)}")

            # 권한 체크
            try:
                if os.path.exists(library_path):
                    if os.access(library_path, os.W_OK):
                        return (
                            f"{library_path} 경로에 쓰기 권한이 있습니다.",
                            "tick-circle",
                            "green",
                            {"display": "block"},
                            library_name,
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                            cells,
                        )
                    else:
                        return (
                            f"{library_path} 경로에 쓰기 권한이 없습니다.",
                            "warning-sign",
                            "orange",
                            {"display": "block"},
                            library_name,
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                            cells,
                        )
                else:
                    if os.access(signoff_path, os.W_OK):
                        return (
                            f"{library_path} 경로가 없습니다. 새로 생성할 수 있습니다.",
                            "info-sign",
                            "blue",
                            {"display": "block"},
                            library_name,
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                            cells,
                        )
                    else:
                        return (
                            f"{signoff_path} 경로에 쓰기 권한이 없어 라이브러리 디렉토리를 생성할 수 없습니다.",
                            "warning-sign",
                            "orange",
                            {"display": "block"},
                            library_name,
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                            cells,
                        )
            except Exception as e:
                return (f"권한 확인 중 오류 발생: {str(e)}", "error", "red", {"display": "block"}, library_name, {"display": "inline-flex"}, {"display": "inline-flex"}, cells)

        # 경로 부분 업데이트 콜백
        @app.callback(
            Output("workspace-path-parts", "data", allow_duplicate=True),
            [
                Input("library-name-select", "value"),
                Input("new-library-input", "value"),
            ],
            State("workspace-path-parts", "data"),
            prevent_initial_call=True,
        )
        def update_path_parts_library(selected_lib, new_lib, current_parts):
            library_name = selected_lib if selected_lib else new_lib
            if not library_name:
                return current_parts

            updated_parts = current_parts.copy()
            updated_parts["library"] = library_name
            return updated_parts

        # 셀 선택 또는 입력 시 권한 체크
        @app.callback(
            [
                Output("cell-permission-status", "children"),
                Output("cell-permission-icon", "icon"),
                Output("cell-permission-icon", "color"),
                Output("cell-permission-box", "style"),
                Output("current-cell-badge", "children"),
                Output("current-cell-badge", "style"),
                Output("cell-separator", "style"),
                Output("current-user-badge", "style"),
            ],
            [
                Input("cell-name-select", "value"),
                Input("new-cell-input", "value"),
            ],
            [
                State("mounted-storage-select", "value"),
                State("library-name-select", "value"),
                State("new-library-input", "value"),
                State("workspace-path-parts", "data"),
            ],
            prevent_initial_call=True,
        )
        def handle_cell_selection(selected_cell, new_cell, storage_path, selected_lib, new_lib, path_parts):
            if not storage_path:
                raise exceptions.PreventUpdate

            library_name = selected_lib if selected_lib else new_lib
            if not library_name:
                raise exceptions.PreventUpdate

            # 선택 또는 입력된 셀 이름 결정
            cell_name = selected_cell if selected_cell else new_cell
            if not cell_name:
                return ("", "", "", {"display": "none"}, "", {"display": "none"}, {"display": "none"}, {"display": "none"})

            # 경로 구성
            library_path = os.path.join(storage_path, "SIGNOFF", library_name)
            cell_path = os.path.join(library_path, cell_name)

            # 권한 체크
            try:
                if os.path.exists(cell_path):
                    if os.access(cell_path, os.W_OK):
                        return (
                            f"{cell_path} 경로에 쓰기 권한이 있습니다.",
                            "tick-circle",
                            "green",
                            {"display": "block"},
                            cell_name,
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                        )
                    else:
                        return (
                            f"{cell_path} 경로에 쓰기 권한이 없습니다.",
                            "warning-sign",
                            "orange",
                            {"display": "block"},
                            cell_name,
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                        )
                else:
                    if os.access(library_path, os.W_OK):
                        return (
                            f"{cell_path} 경로가 없습니다. 새로 생성할 수 있습니다.",
                            "info-sign",
                            "blue",
                            {"display": "block"},
                            cell_name,
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                        )
                    else:
                        return (
                            f"{library_path} 경로에 쓰기 권한이 없어 셀 디렉토리를 생성할 수 없습니다.",
                            "warning-sign",
                            "orange",
                            {"display": "block"},
                            cell_name,
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                            {"display": "inline-flex"},
                        )
            except Exception as e:
                return (
                    f"권한 확인 중 오류 발생: {str(e)}",
                    "error",
                    "red",
                    {"display": "block"},
                    cell_name,
                    {"display": "inline-flex"},
                    {"display": "inline-flex"},
                    {"display": "inline-flex"},
                )

        # 경로 부분 업데이트 콜백 (셀)
        @app.callback(
            Output("workspace-path-parts", "data", allow_duplicate=True),
            [
                Input("cell-name-select", "value"),
                Input("new-cell-input", "value"),
            ],
            State("workspace-path-parts", "data"),
            prevent_initial_call=True,
        )
        def update_path_parts_cell(selected_cell, new_cell, current_parts):
            cell_name = selected_cell if selected_cell else new_cell
            if not cell_name:
                return current_parts

            updated_parts = current_parts.copy()
            updated_parts["cell"] = cell_name
            return updated_parts

        # 서로 선택 영향 - Library 선택 시 Cell 입력 초기화
        @app.callback(
            [
                Output("cell-name-select", "value", allow_duplicate=True),
                Output("new-cell-input", "value"),
            ],
            [
                Input("library-name-select", "value"),
                Input("new-library-input", "value"),
            ],
            prevent_initial_call=True,
        )
        def reset_cell_inputs(lib_select, lib_input):
            return None, ""

        # 최종 경로 표시
        @app.callback(
            Output("final-workspace-path", "children"),
            Output("final-path-alert", "color"),
            Output("final-path-alert", "title"),
            Input("workspace-stepper", "active"),
            State("workspace-path-parts", "data"),
            prevent_initial_call=True,
        )
        def update_final_path(active_step, path_parts):
            if active_step != 2 or not path_parts:
                raise exceptions.PreventUpdate

            storage = path_parts.get("storage", "")
            library = path_parts.get("library", "")
            cell = path_parts.get("cell", "")
            user = path_parts.get("user", os.getenv("USER", "unknown"))

            final_path = os.path.join(storage, "SIGNOFF", library, cell, user)

            # 경로 존재 및 권한 확인
            if os.path.exists(final_path):
                if os.access(final_path, os.W_OK):
                    return final_path, "green", "✓ 경로가 이미 존재하며 쓰기 권한이 있습니다"
                else:
                    return final_path, "red", "⚠️ 경로가 존재하지만 쓰기 권한이 없습니다"
            else:
                parent_dir = os.path.dirname(final_path)
                if os.path.exists(parent_dir) and os.access(parent_dir, os.W_OK):
                    return final_path, "blue", "ℹ️ 경로가 없습니다. 새로 생성할 수 있습니다"
                else:
                    return final_path, "orange", "⚠️ 경로 생성을 위한 상위 디렉토리 권한이 불충분합니다"

        # 사용자 정의 경로 토글
        @app.callback(
            Output("custom-path-collapse", "opened"),
            Output("toggle-custom-path-button", "rightSection"),
            Output("toggle-custom-path-button", "children"),
            Input("toggle-custom-path-button", "n_clicks"),
            State("custom-path-collapse", "opened"),
            prevent_initial_call=True,
        )
        def toggle_custom_path(n_clicks, is_open):
            if not n_clicks:
                raise exceptions.PreventUpdate

            if is_open:
                return False, dbpc.Icon(icon="caret-down", size=12), "사용자 정의 경로 사용"
            else:
                return True, dbpc.Icon(icon="caret-up", size=12), "단계별 설정으로 돌아가기"

        # 사용자 정의 경로 유효성 검사
        @app.callback(
            [
                Output("custom-path-status", "children"),
                Output("custom-path-permission-icon", "icon"),
                Output("custom-path-permission-icon", "color"),
                Output("custom-path-permission-box", "style"),
                Output("apply-custom-path-btn", "disabled"),
            ],
            Input("custom-workspace-path", "value"),
            prevent_initial_call=True,
        )
        def validate_custom_path(path):
            if not path:
                return "", "", "", {"display": "none"}, True

            is_valid, message, status = self.validate_workspace_path(path)

            icon = "tick-circle" if status == "success" else "warning-sign" if status == "warning" else "error"
            color = "green" if status == "success" else "orange" if status == "warning" else "red"

            return message, icon, color, {"display": "block"}, not is_valid

        # Stepper 이동 버튼 제어
        @app.callback(
            [
                Output("workspace-stepper", "active"),
                Output("stepper-prev-button", "disabled"),
                Output("stepper-next-button", "disabled"),
                Output("stepper-next-button", "children"),
            ],
            [
                Input("stepper-prev-button", "n_clicks"),
                Input("stepper-next-button", "n_clicks"),
            ],
            [
                State("workspace-stepper", "active"),
                State("mounted-storage-select", "value"),
                State("library-name-select", "value"),
                State("cell-name-select", "value"),
                State("workspace-path-parts", "data"),
            ],
            prevent_initial_call=True,
        )
        def handle_stepper_buttons(prev_clicks, next_clicks, current_step, storage, library, cell, path_parts):
            triggered_id = ctx.triggered_id

            if triggered_id == "stepper-prev-button" and prev_clicks:
                new_step = max(0, current_step - 1)
                # 이전 단계로 돌아갈 때는 버튼 상태 설정
                prev_disabled = new_step == 0
                next_disabled = False  # 이전으로 갈 때는 항상 '다음' 활성화
                button_text = "다음"

                return new_step, prev_disabled, next_disabled, button_text

            elif triggered_id == "stepper-next-button" and next_clicks:
                # 다음 단계로 갈 때는 유효성 검사
                if current_step == 0:
                    # 스토리지 선택 검증
                    if not storage:
                        raise exceptions.PreventUpdate
                    new_step = 1

                elif current_step == 1:
                    # 라이브러리와 셀 선택 검증
                    if not library or not cell:
                        raise exceptions.PreventUpdate
                    new_step = 2

                else:
                    # 최종 단계 - 워크스페이스 설정
                    new_step = 2  # 유지 (최종 단계에서 설정 완료 버튼이 별도로 처리)

                is_final = new_step == 2
                prev_disabled = False
                next_disabled = False
                button_text = "워크스페이스 설정" if is_final else "다음"

                return new_step, prev_disabled, next_disabled, button_text

            raise exceptions.PreventUpdate

        # 다음 버튼 활성화 제어
        @app.callback(
            Output("stepper-next-button", "disabled", allow_duplicate=True),
            [
                Input("mounted-storage-select", "value"),
                Input("library-name-select", "value"),
                Input("cell-name-select", "value"),
            ],
            State("workspace-stepper", "active"),
            prevent_initial_call=True,
        )
        def update_next_button_state(storage, library, cell, current_step):
            # 각 단계별 필수 입력값 확인
            if current_step == 0:
                return storage is None  # 스토리지 선택이 없으면 비활성화
            elif current_step == 1:
                return not (library and cell)  # 라이브러리와 셀 모두 선택해야 활성화
            else:
                return False  # 마지막 단계에서는 항상 활성화

        # 최종 워크스페이스 설정 (표준 경로)
        @app.callback(
            [
                Output("workspace-setup-modal", "opened", allow_duplicate=True),
                Output("workspace-path", "value", allow_duplicate=True),
                Output("workspace-display-indicator", "children", allow_duplicate=True),
                Output("workspace-drawer", "title", allow_duplicate=True),
                Output("workspace-display-indicator", "label", allow_duplicate=True),
                Output("workspace-contents", "children", allow_duplicate=True),
                Output("workspace-stepper-alert", "style", allow_duplicate=True),
                Output("workspace-stepper-alert", "children", allow_duplicate=True),
            ],
            Input("stepper-next-button", "n_clicks"),
            [
                State("workspace-stepper", "active"),
                State("workspace-path-parts", "data"),
                State("stepper-next-button", "children"),
            ],
            prevent_initial_call=True,
        )
        def setup_standard_workspace(next_clicks, active_step, path_parts, button_text):
            # 최종 설정 버튼 클릭 시에만 처리
            if active_step != 2 or button_text != "워크스페이스 설정" or not next_clicks:
                raise exceptions.PreventUpdate

            # 경로 구성
            storage = path_parts.get("storage", "")
            library = path_parts.get("library", "")
            cell = path_parts.get("cell", "")
            user = path_parts.get("user", os.getenv("USER", "unknown"))

            if not storage or not library or not cell:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, "경로 설정이 불완전합니다. 모든 단계를 완료해주세요.")  # 모달 유지  # 오류 메시지 표시

            path = os.path.join(storage, "SIGNOFF", library, cell, user)

            # 경로 유효성 검사
            is_valid, message, status = self.validate_workspace_path(path)
            if not is_valid:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, message)  # 모달 유지  # 오류 메시지 표시

            # 경로 생성
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, f"디렉토리 생성 중 오류 발생: {str(e)}")

            # 설정 파일 업데이트
            if set_workspace_dir(path):
                global WORKSPACE_DIR
                WORKSPACE_DIR = path

                # 워크스페이스 내용 가져오기
                try:
                    contents = self._get_directory_contents(path)
                except Exception as e:
                    contents = [dmc.Text(f"Error reading directory: {str(e)}", c="red")]

                return (
                    False,  # 모달 닫기
                    path,  # workspace-path 업데이트
                    os.path.basename(path),  # workspace-display-indicator 업데이트
                    path,  # workspace-drawer 제목 업데이트
                    str(get_job_count()),  # workspace-display-indicator 라벨 업데이트
                    contents,  # workspace-contents 업데이트
                    {"display": "none"},  # 오류 메시지 숨기기
                    no_update,
                )
            else:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, "워크스페이스 설정을 저장하지 못했습니다.")

        # 사용자 정의 경로로 워크스페이스 설정
        @app.callback(
            [
                Output("workspace-setup-modal", "opened", allow_duplicate=True),
                Output("workspace-path", "value", allow_duplicate=True),
                Output("workspace-display-indicator", "children", allow_duplicate=True),
                Output("workspace-drawer", "title", allow_duplicate=True),
                Output("workspace-display-indicator", "label", allow_duplicate=True),
                Output("workspace-contents", "children", allow_duplicate=True),
                Output("workspace-stepper-alert", "style", allow_duplicate=True),
                Output("workspace-stepper-alert", "children", allow_duplicate=True),
            ],
            Input("apply-custom-path-btn", "n_clicks"),
            State("custom-workspace-path", "value"),
            prevent_initial_call=True,
        )
        def setup_custom_workspace(n_clicks, custom_path):
            if not n_clicks or not custom_path:
                raise exceptions.PreventUpdate

            # 경로 유효성 검사
            is_valid, message, status = self.validate_workspace_path(custom_path)
            if not is_valid:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, message)  # 모달 유지  # 오류 메시지 표시

            # 경로 생성
            try:
                os.makedirs(custom_path, exist_ok=True)
            except Exception as e:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, f"디렉토리 생성 중 오류 발생: {str(e)}")

            # 설정 파일 업데이트
            if set_workspace_dir(custom_path):
                global WORKSPACE_DIR
                WORKSPACE_DIR = custom_path

                # 워크스페이스 내용 가져오기
                try:
                    contents = self._get_directory_contents(custom_path)
                except Exception as e:
                    contents = [dmc.Text(f"Error reading directory: {str(e)}", c="red")]

                return (
                    False,  # 모달 닫기
                    custom_path,  # workspace-path 업데이트
                    os.path.basename(custom_path),  # workspace-display-indicator 업데이트
                    custom_path,  # workspace-drawer 제목 업데이트
                    str(get_job_count()),  # workspace-display-indicator 라벨 업데이트
                    contents,  # workspace-contents 업데이트
                    {"display": "none"},  # 오류 메시지 숨기기
                    no_update,
                )
            else:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, "워크스페이스 설정을 저장하지 못했습니다.")

        # 최종 워크스페이스 설정
        @app.callback(
            Output("workspace-setup-modal", "opened", allow_duplicate=True),
            Output("workspace-path", "value", allow_duplicate=True),
            Output("workspace-display-indicator", "children", allow_duplicate=True),
            Output("workspace-drawer", "title", allow_duplicate=True),
            Output("workspace-display-indicator", "label", allow_duplicate=True),
            Output("workspace-contents", "children", allow_duplicate=True),
            Output("workspace-stepper-alert", "style", allow_duplicate=True),
            Output("workspace-stepper-alert", "children", allow_duplicate=True),
            Input("stepper-next-button", "n_clicks"),
            Input("apply-custom-path-btn", "n_clicks"),
            State("workspace-stepper", "active"),
            State("workspace-path-parts", "data"),
            State("custom-workspace-path", "value"),
            prevent_initial_call=True,
        )
        def setup_workspace(next_clicks, custom_clicks, active_step, path_parts, custom_path):
            triggered_id = ctx.triggered_id

            # 경로 결정
            if triggered_id == "stepper-next-button" and active_step == 3:
                # Stepper 완료
                storage = path_parts.get("storage", "")
                library = path_parts.get("library", "")
                cell = path_parts.get("cell", "")
                user = path_parts.get("user", os.getenv("USER", "unknown"))

                path = os.path.join(storage, "SIGNOFF", library, cell, user)
            elif triggered_id == "apply-custom-path-btn":
                # 사용자 정의 경로
                path = custom_path
            else:
                raise exceptions.PreventUpdate

            # 경로 유효성 검사
            is_valid, message, status = self.validate_workspace_path(path)
            if not is_valid:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, message)  # 모달 유지  # 오류 메시지 표시

            # 경로 생성
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, f"디렉토리 생성 중 오류 발생: {str(e)}")

            # 설정 파일 업데이트
            if set_workspace_dir(path):
                global WORKSPACE_DIR
                WORKSPACE_DIR = path

                # 워크스페이스 내용 가져오기
                try:
                    contents = self._get_directory_contents(path)
                except Exception as e:
                    contents = [dmc.Text(f"Error reading directory: {str(e)}", c="red")]

                return (
                    False,  # 모달 닫기
                    path,  # workspace-path 업데이트
                    os.path.basename(path),  # workspace-display-indicator 업데이트
                    path,  # workspace-drawer 제목 업데이트
                    str(get_job_count()),  # workspace-display-indicator 라벨 업데이트
                    contents,  # workspace-contents 업데이트
                    {"display": "none"},  # 오류 메시지 숨기기
                    no_update,
                )
            else:
                return (True, no_update, no_update, no_update, no_update, no_update, {"display": "block"}, "워크스페이스 설정을 저장하지 못했습니다")

        # Library 관련 콜백 - 새 Library 생성 UI 활성화/비활성화
        @app.callback(
            [
                Output("new-library-input", "disabled"),
                Output("confirm-new-library-btn", "disabled"),
                Output("cancel-new-library-btn", "disabled"),
                Output("library-name-select", "disabled"),
                Output("create-new-library-btn", "disabled"),
            ],
            Input("create-new-library-btn", "n_clicks"),
            Input("cancel-new-library-btn", "n_clicks"),
            State("mounted-storage-select", "value"),
            prevent_initial_call=True,
        )
        def toggle_new_library_inputs(create_clicks, cancel_clicks, storage_path):
            triggered_id = ctx.triggered_id

            if not storage_path:
                raise exceptions.PreventUpdate

            if triggered_id == "create-new-library-btn" and create_clicks:
                # 새 Library 생성 모드
                return False, False, False, True, True  # 입력 활성화, 선택 비활성화
            elif triggered_id == "cancel-new-library-btn" and cancel_clicks:
                # 취소 - 선택 모드로 돌아감
                return True, True, True, False, False  # 입력 비활성화, 선택 활성화

            raise exceptions.PreventUpdate

        # 새 Library 생성 처리
        @app.callback(
            [
                Output("library-name-select", "data", allow_duplicate=True),
                Output("library-name-select", "value"),
                Output("new-library-input", "value", allow_duplicate=True),
                Output("new-library-input", "disabled", allow_duplicate=True),
                Output("confirm-new-library-btn", "disabled", allow_duplicate=True),
                Output("cancel-new-library-btn", "disabled", allow_duplicate=True),
                Output("library-name-select", "disabled", allow_duplicate=True),
                Output("create-new-library-btn", "disabled", allow_duplicate=True),
                Output("library-permission-status", "children", allow_duplicate=True),
                Output("library-permission-icon", "icon", allow_duplicate=True),
                Output("library-permission-icon", "color", allow_duplicate=True),
                Output("library-permission-box", "style", allow_duplicate=True),
            ],
            Input("confirm-new-library-btn", "n_clicks"),
            State("new-library-input", "value"),
            State("mounted-storage-select", "value"),
            State("library-name-select", "data"),
            prevent_initial_call=True,
        )
        def create_new_library(n_clicks, new_library, storage_path, current_libraries):
            if not n_clicks or not new_library or not storage_path:
                raise exceptions.PreventUpdate

            # 경로 유효성 확인
            signoff_path = os.path.join(storage_path, "SIGNOFF")
            new_library_path = os.path.join(signoff_path, new_library)

            try:
                # 이미 존재하는지 확인
                if os.path.exists(new_library_path):
                    return (current_libraries, new_library, "", True, True, True, False, False, f"{new_library_path} 경로가 이미 존재합니다.", "info-sign", "blue", {"display": "block"})

                # 디렉토리 생성 권한 확인
                if not os.access(signoff_path, os.W_OK):
                    return (
                        current_libraries,
                        None,
                        "",
                        True,
                        True,
                        True,
                        False,
                        False,
                        f"{signoff_path} 경로에 쓰기 권한이 없어 Library를 생성할 수 없습니다.",
                        "warning-sign",
                        "red",
                        {"display": "block"},
                    )

                # 디렉토리 생성
                os.makedirs(new_library_path, exist_ok=True)

                # 라이브러리 목록 업데이트
                updated_libraries = current_libraries.copy() if current_libraries else []
                updated_libraries.append({"value": new_library, "label": new_library})

                return (updated_libraries, new_library, "", True, True, True, False, False, f"{new_library_path} 경로가 생성되었습니다.", "tick-circle", "green", {"display": "block"})
            except Exception as e:
                return (current_libraries, None, "", True, True, True, False, False, f"Library 생성 중 오류 발생: {str(e)}", "error", "red", {"display": "block"})

        # Cell 선택 활성화 콜백
        @app.callback(
            [
                Output("cell-name-select", "disabled"),
                Output("create-new-cell-btn", "disabled"),
            ],
            Input("library-name-select", "value"),
            State("mounted-storage-select", "value"),
            prevent_initial_call=True,
        )
        def enable_cell_selection(library, storage):
            if not library or not storage:
                return True, True

            # Library 경로 권한 체크
            library_path = os.path.join(storage, "SIGNOFF", library)
            if os.path.exists(library_path) and os.access(library_path, os.W_OK):
                return False, False  # 셀 선택 활성화

            return True, True  # 쓰기 권한이 없으면 비활성화 유지

        # Cell 관련 콜백 - 새 Cell 생성 UI 활성화/비활성화
        @app.callback(
            [
                Output("new-cell-input", "disabled"),
                Output("confirm-new-cell-btn", "disabled"),
                Output("cancel-new-cell-btn", "disabled"),
                Output("cell-name-select", "disabled", allow_duplicate=True),
                Output("create-new-cell-btn", "disabled", allow_duplicate=True),
            ],
            Input("create-new-cell-btn", "n_clicks"),
            Input("cancel-new-cell-btn", "n_clicks"),
            State("library-name-select", "value"),
            prevent_initial_call=True,
        )
        def toggle_new_cell_inputs(create_clicks, cancel_clicks, library):
            triggered_id = ctx.triggered_id

            if not library:
                raise exceptions.PreventUpdate

            if triggered_id == "create-new-cell-btn" and create_clicks:
                # 새 Cell 생성 모드
                return False, False, False, True, True  # 입력 활성화, 선택 비활성화
            elif triggered_id == "cancel-new-cell-btn" and cancel_clicks:
                # 취소 - 선택 모드로 돌아감
                return True, True, True, False, False  # 입력 비활성화, 선택 활성화

            raise exceptions.PreventUpdate

        # 새 Cell 생성 처리
        @app.callback(
            [
                Output("cell-name-select", "data", allow_duplicate=True),
                Output("cell-name-select", "value", allow_duplicate=True),
                Output("new-cell-input", "value", allow_duplicate=True),
                Output("new-cell-input", "disabled", allow_duplicate=True),
                Output("confirm-new-cell-btn", "disabled", allow_duplicate=True),
                Output("cancel-new-cell-btn", "disabled", allow_duplicate=True),
                Output("cell-name-select", "disabled", allow_duplicate=True),
                Output("create-new-cell-btn", "disabled", allow_duplicate=True),
                Output("cell-permission-status", "children", allow_duplicate=True),
                Output("cell-permission-icon", "icon", allow_duplicate=True),
                Output("cell-permission-icon", "color", allow_duplicate=True),
                Output("cell-permission-box", "style", allow_duplicate=True),
            ],
            Input("confirm-new-cell-btn", "n_clicks"),
            State("new-cell-input", "value"),
            State("mounted-storage-select", "value"),
            State("library-name-select", "value"),
            State("cell-name-select", "data"),
            prevent_initial_call=True,
        )
        def create_new_cell(n_clicks, new_cell, storage_path, library, current_cells):
            if not n_clicks or not new_cell or not storage_path or not library:
                raise exceptions.PreventUpdate

            # 경로 유효성 확인
            library_path = os.path.join(storage_path, "SIGNOFF", library)
            new_cell_path = os.path.join(library_path, new_cell)

            try:
                # 이미 존재하는지 확인
                if os.path.exists(new_cell_path):
                    return (current_cells, new_cell, "", True, True, True, False, False, f"{new_cell_path} 경로가 이미 존재합니다.", "info-sign", "blue", {"display": "block"})

                # 디렉토리 생성 권한 확인
                if not os.access(library_path, os.W_OK):
                    return (current_cells, None, "", True, True, True, False, False, f"{library_path} 경로에 쓰기 권한이 없어 Cell을 생성할 수 없습니다.", "warning-sign", "red", {"display": "block"})

                # 디렉토리 생성
                os.makedirs(new_cell_path, exist_ok=True)

                # 셀 목록 업데이트
                updated_cells = current_cells.copy() if current_cells else []
                updated_cells.append({"value": new_cell, "label": new_cell})

                return (updated_cells, new_cell, "", True, True, True, False, False, f"{new_cell_path} 경로가 생성되었습니다.", "tick-circle", "green", {"display": "block"})
            except Exception as e:
                return (current_cells, None, "", True, True, True, False, False, f"Cell 생성 중 오류 발생: {str(e)}", "error", "red", {"display": "block"})

        # 3단계에서 RUNSCRIPT 폴더 체크
        @app.callback(
            [
                Output("runscript-check-status", "children"),
                Output("runscript-check-icon", "icon"),
                Output("runscript-check-icon", "color"),
                Output("runscript-check-box", "style"),
            ],
            Input("workspace-stepper", "active"),
            State("workspace-path-parts", "data"),
            prevent_initial_call=True,
        )
        def check_runscript_folder(active_step, path_parts):
            if active_step != 2 or not path_parts:
                return "", "", "", {"display": "none"}

            storage = path_parts.get("storage", "")
            library = path_parts.get("library", "")
            cell = path_parts.get("cell", "")
            user = path_parts.get("user", os.getenv("USER", "unknown"))

            final_path = os.path.join(storage, "SIGNOFF", library, cell, user)
            runscript_path = os.path.join(final_path, "RUNSCRIPTS")

            try:
                if os.path.exists(runscript_path) and os.path.isdir(runscript_path):
                    # RUNSCRIPTS 폴더의 내용 확인
                    runscripts = [f for f in os.listdir(runscript_path) if os.path.isdir(os.path.join(runscript_path, f))]

                    if runscripts:
                        return (
                            f"RUNSCRIPTS 폴더가 존재하며 {len(runscripts)}개의 Signoff Application이 있습니다: {', '.join(runscripts[:3])}{'...' if len(runscripts) > 3 else ''}",
                            "tick-circle",
                            "green",
                            {"display": "block"},
                        )
                    else:
                        return ("RUNSCRIPTS 폴더가 존재하지만 Signoff Application이 없습니다.", "info-sign", "blue", {"display": "block"})
                else:
                    return ("RUNSCRIPTS 폴더가 존재하지 않습니다. 설정 후 첫 실행 시 자동으로 생성됩니다.", "info-sign", "blue", {"display": "block"})
            except Exception as e:
                return (f"RUNSCRIPTS 폴더 확인 중 오류 발생: {str(e)}", "warning-sign", "orange", {"display": "block"})
```

## File: workspace/LS_SSPHVCT_20250318_01/job_config.yaml
```yaml
app: LS
corners:
  process: SSP
  temperature: CT
  voltage: HV
inputs:
  CT: -10
  Default_Voltage: -0.96
  Discard_Subckt_File: ''
  EDR_File: /user/LINK_EDR
  HV_GND_List_File: /user/veri/HV_GND_List.inc
  HV_VDD_List_File: /user/veri/HV_VDD_List.inc
  Input_Clock_Period: 4
  Input_Slope: 0.4
  MP_File: /user/LINK_MP
  Netlist_File: /user/l432gx.star
  Rpass_File: /user/drPASS.lib
  Simulation_Time: 10
  Simulation_Time_Step: 0.01
  UserDefine_Corner: ''
job_finish_time: '2025-03-18 14:14:13'
job_id: null
job_start_time: '2025-03-18 14:12:37'
message: Simulation failed
name: LS_SSPHVCT_20250318_01
output_filename: result
owner: deepwonwoo
pid: 1051921
status: failed
workspace: /user/so/launcher/SOL_deepwonwoo/workspace/LS_SSPHVCT_20250318_01
```

## File: app.py
```python
import os
import argparse
import dash_mantine_components as dmc
import dash_blueprint_components as dbpc
from flask import Flask
from flaskwebgui import FlaskUI
from diskcache import Cache
from dash import Dash, html, Input, Output, callback, ctx, no_update, set_props, dcc, DiskcacheManager, _dash_renderer

from job_set.page import SetPage
from job_run.page import RunPage
from utils.settings import APPCACHE_DIR
from utils.workspace import WorkspaceDrawer, get_workspace_dir, get_job_count, set_workspace_dir
from utils.logger import logger

s


def create_navbar():
    """Create the navigation bar component"""
    navbar_children = [
        dmc.GridCol(
            dmc.Group(
                [
                    dbpc.EntityTitle(
                        title="Signoff Launcher",
                        heading="H2",
                        style={"overflow": "hidden", "text-overflow": "ellipsis", "white-space": "nowrap"},
                    ),
                    dmc.Group(
                        [
                            dbpc.Button(id="set-page-btn", icon="rocket", text="Set", minimal=True, large=True),
                            dbpc.Button(id="run-page-btn", icon="rocket-slant", text="Run", minimal=True, large=True),
                        ],
                        gap="sm",
                    ),
                ],
                align="flex-start",
            ),
            span=6,
        ),
        dmc.GridCol(
            dmc.Group(
                [
                    dbpc.Button(
                        dmc.Indicator(
                            get_workspace_dir().replace(os.getcwd(), "").replace("/user/", "").replace("/VERIFY/SIGNOFF", ""),
                            color="indigo",
                            id="workspace-display-indicator",
                            inline=True,
                            label=get_job_count(),
                            size=16,
                        ),
                        id="workspace-btn",
                        icon="projects",
                        minimal=True,
                        large=True,
                    ),
                    dbpc.Button(text="", id="baap-btn", icon="link", minimal=True, large=True),
                ],
                justify="flex-end",
                gap="sm",
            ),
            span=6,
        ),
    ]

    return dbpc.Navbar(
        dmc.Grid(
            children=navbar_children,
            gutter="xl",
            style={"height": "100%", "padding": "0 20px"},
        ),
        fixedToTop=True,
        style={"box-shadow": "0 2px 4px", "height": "50px", "z-index": 1000, "minWidth": "1200px"},
    )


def init_dash_app(server: Flask) -> Dash:
    """Initialize and configure Dash application"""
    return Dash(
        server=server,
        title="Signoff Launcher",
        suppress_callback_exceptions=True,
        prevent_initial_callbacks=True,
        background_callback_manager=DiskcacheManager(Cache(DISK_CACHE)),
    )


def create_app(initial_workspace=None):
    """Create and configure the application"""
    if initial_workspace:
        try:
            scuccess = set_workspace_dir(initial_workspace)
            if scuccess:
                logger.info(f"Workspace initialized to : {initial_workspace}")
            else:
                logger.error(f"Failed to initialize workspace to : {initial_workspace}")
        except Exception as e:
            logger.error(f"Error setting initial workspace: {str(e)}, exc_info=True")

    # Initialize Flask and Dash
    server = Flask(__name__)
    app = init_dash_app(server)

    # Initialize pages and settings
    set_page = SetPage(app)
    run_page = RunPage(app)
    workspace_manager = WorkspaceDrawer(app)

    # Set up main layout
    app.layout = dmc.MantineProvider(
        html.Div(
            [
                create_navbar(),
                html.Div(set_page.layout(), id="page-content", style={"paddingTop": 60}),
                workspace_manager.layout(),
                # workspace_manager.workspace_setup_modal(),
                dbpc.Alert(
                    id="job-created-alert",
                    cancelButtonText="Stay at Set Page",
                    confirmButtonText="Move to Run Page",
                    icon="cube-add",
                    intent="success",
                ),
                dbpc.Alert(
                    id="job-rerun-alert",
                    icon="info-sign",
                    cancelButtonText="Staty at Runn Page",
                    confirmButtonText="Move to SetPage",
                    intent="success",
                    isOpen=False,
                    children="",
                ),
            ],
            style={"minWidth": "1200px"},
        )
    )

    app = register_callbacks(app, set_page, run_page)
    return app, server


# Callback Registration
def register_callbacks(app: Dash, set_page, run_page) -> Dash:
    @app.callback(
        Output("page-content", "children"),
        Output("current-page-store", "data"),
        Output("job-created-alert", "isConfirmed"),
        Output("job-rerun-alert", "isConfirmed"),
        Output("job-rerun-alert", "isOpen", allow_duplicate=True),
        Input("set-page-btn", "n_clicks"),
        Input("run-page-btn", "n_clicks"),
        Input("job-created-alert", "isConfirmed"),
        Input("job-rerun-alert", "isConfirmed"),
        State("current-page-store", "data"),
        prevent_initial_call=True,
    )
    def handle_page_navigation(set_clicks, run_clicks, move_runpage, move_setpage, current_page):
        print(f"handle_page_navigation: {set_clicks} {run_clicks}")
        try:
            trigger = ctx.triggered_id
            logger.debug(f"Handle navigation between pages : {trigger}")

            # 현재 페이지가 없으면 기본값 설정
            if current_page is None:
                current_page = "set"  # 기본 페이지

            if trigger == "set-page-btn":
                # 이미 set page에 있으면 아무것도 하지 않음
                print(f"current_page{current_page}")
                if current_page == "set":
                    return no_update, "set", no_update, no_update, no_update
                return set_page.layout(), "set", no_update, no_update, no_update

            elif trigger == "run-page-btn":
                if current_page == "run":
                    return no_update, "run", no_update, no_update, no_update
                return run_page.layout(), "run", no_update, no_update, no_update

            elif trigger == "job-created-alert" and move_runpage:
                return run_page.layout(), "run", False, no_update, no_update

            elif trigger == "job-rerun-alert" and move_setpage:
                return set_page.layout(), "set", False, False, False

            return no_update, current_page, no_update, no_update, no_update

        except Exception as e:
            logger.error(f"Error in navigation callback: {str(e)}", exc_info=True)
            return no_update, no_update, no_update, no_update, no_update

    return app


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Signoff Launcher")
    parser.add_argument("-workspace", "--workspace", type=str, help="Specify initial workspace directory path")
    args = parser.parse_args()

    app, application = create_app(initial_workspace=args.workspace)

    # if ENABLE_MONITORING:
    #    import threading
    #    import psutil
    #    app_process = psutil.Process()
    #    monitor_thread = threading.Thread(target=resource_monitor, args=(app_process,))
    #    monitor_thread.daemon = True  # Stop monitoring when app exits
    #    monitor_thread.start()

    app.run(debug=True)

    # flask_ui_params = {
    #     "app": application,
    #     "server": "flask",
    # }
    # FlaskUI(**flask_ui_params).run()
```

## File: signoff_applications.yaml
```yaml
# signoff_applications.yaml
applications:
  - name: "CANATR"
    runscript_path: "/user/signoff.dsa/RUNSCRIPTS/signoff-canatr"
  - name: "CDA"
    runscript_path: "/user/signoff.dsa/RUNSCRIPTS/signoff-cda"
  - name: "DCPATH"
    runscript_path: "/user/signoff.dsa/RUNSCRIPTS/signoff-dcpath"
  - name: "DSC"
    runscript_path: "/user/signoff.dsa/RUNSCRIPTS/signoff-dsc"
  - name: "FANOUT"
    runscript_path: "/user/signoff.dsa/RUNSCRIPTS/signoff-fanout"
  - name: "FLOATNODE"
    runscript_path: "/user/signoff.dsa/RUNSCRIPTS/signoff-floatnode"
  - name: "LS"
    runscript_path: "/user/signoff.dsa/RUNSCRIPTS/signoff-ls"
  - name: "LSC"
    runscript_path: "/user/signoff.dsa/RUNSCRIPTS/signoff-lsc"
  - name: "PEC"
    runscript_path: "/user/signoff.dsa/RUNSCRIPTS/signoff-pec"


classification_schemes:
  - name: "HBM FinFET Signoff"
    key: "hbm_finfet_signoff"
    categories:
      - name: "HBM FinFET Signoff"
        applications: ["CANATR", "CDA", "DCPATH", "DRIVER_KEEPER", "DSC", "FANOUT", "FLOATNODE", "LS","LSC","PEC", "PEC_UVD", "PNRATIO", "DYNAMIC_DC_PATH","GLITCH_MARGIN_CHECK_HBM", "PT_SIGNOFF","DYNAMIC_COUPLING_HBM","AUTO_PULSE","TIEHILO_AT_JUNCTION_IN_BDIE","POWER_AT_GATE_PIN_IN_BDIE","PRSIM_BDIE"]
  - name: "DRAM Signoff"
    key: "dram_signoff"
    categories:
      - name: "DRAM Signoff"
        applications: ["CANATR", "CDA", "DCPATH", "DRIVER_KEEPER", "DSC", "FANOUT", "FLOATNODE","LS","LSC","PEC","PEC_UVD","PNRATIO","DYNAMIC_DC_PATH","AUTO_PURSE","PRSIM", "GLITCH_MARGIN_CHECK"]
  - name: "ALL"
    key: "all_signoff"
    categories:
      - name: "Others"
        applications: ["BA_DUMP_NETLIST", "VOLTAGE_FINDER","VBULK_CHECK","REQUEST_FORM_CHECKER", "BLOCK_LEVEL_TR_STA", "GATE_COUNTER_BDIE","GATE_COUNTER_AUTO_STA_BDIE"]
      - name: "HBM"
        applications: ["CANATR", "CDA", "DCPATH", "DRIVER_KEEPER", "DSC", "FANOUT", "FLOATNODE", "LS","LSC","PEC", "PEC_UVD", "PNRATIO", "DYNAMIC_DC_PATH","GLITCH_MARGIN_CHECK_HBM", "PT_SIGNOFF","DYNAMIC_COUPLING_HBM","AUTO_PULSE","TIEHILO_AT_JUNCTION_IN_BDIE","POWER_AT_GATE_PIN_IN_BDIE","PRSIM_BDIE"]
      - name: "DRAM"
        applications: ["CANATR", "CDA", "DCPATH", "DRIVER_KEEPER", "DSC", "FANOUT", "FLOATNODE","LS","LSC","PEC","PEC_UVD","PNRATIO","DYNAMIC_DC_PATH","AUTO_PURSE","PRSIM", "GLITCH_MARGIN_CHECK"]
```
