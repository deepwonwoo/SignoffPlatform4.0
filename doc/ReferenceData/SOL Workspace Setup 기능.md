첨부로 제공한  sol_workspace_setup.py python코드는 tkinter기반의 나의 signoff launcher workspace를 설정해주는 GUI야.

이 gui를 통해 launcher를 실행하기 전에 표준 workspace 경로 구조를 설정하고 return 받아서 signoff launcher를 수행하게 하고 있어.
local filesystem의 /user/ 에 많은 project 계정 storage들이 mount되어 있고, 이 storage의 계정 경로에서는 VERIFY폴더 안에 SIGNOFF 폴더가 있고 Signoff Launcher는 이를 활용하여 launcher의 workspace를 Library/CELL/ 조구의 폴더를 만들고 마지막에 본인 USER ID 기반의 폴더를 만들어서 거기서 signoff launcher 작업들을 수행하도록 유도하고 있어. 


다음은 sol_workspace_setup.py 했을때의 개발 사양 및 설정들에 대한 내용이야.

<구현한 Sol Workspace 설정 기능들>

* Signoff Launcher 실행 전에 tkinter 기반 Workspace 설정 GUI를 통해 사용자가 표준 workspace 구조("/user/{STORAGE}/VERIFY/SIGNOFF/{LIBRARY}/{CELL}/{USER}")를 설정하고, 이를  signoff launcher에 인자로 전달하는 용도
* 워크스페이스 표준 경로 구조 :  `/user/{STORAGE}/VERIFY/SIGNOFF/{LIBRARY}/{CELL}/{USER}`
* 경로 유효성 검사를 함. (경로 파싱, 디렉토리 확인, 권한 확인 로직 )
* 유효성 검사 통과하면 버튼 활성화
* 기존에 선택하려는 경로가 없다면 생성 가능 여부 확인하고 생성.
*  스토리지 디렉토리(PRJ 계정) 로드 시,  `/user/` 에서 검색 및 권한 확인 
* setting json을 읽어서 이전에 설정했었던 워크스페이스 경로를 불러올수있음.
* 설정 JSON 예시: 
```json
{
  "WORKSPACE_DIR": "/user/storage1/VERIFY/SIGNOFF/LIBRARY1/CELL1/username",
  "HISTORY_WORKSPACE_DIRS": [
  {
	  "path": "/user/storage1/VERIFY/SIGNOFF/LIBRARY1/CELL2/username",
	  "last_used": "2025-06-23 11:05:09"
  },
{
	  "path": "/user/storage1/VERIFY/SIGNOFF/LIBRARY1/CELL3/username",
	  "last_used": "2025-06-23 10:00:19"
  },
  ]
}
```

* GUI 레이아웃:  Cadence Virtuso Library Manager 스타일의 UI 참고
	- 4 섹션으로 구성:
	    1. **상단 섹션**: 현재 선택된 경로 표시 및 직접 편집 필드 , 확인/취소 버튼
	    2. **최근 경로 섹션**: 과거 사용 workspace 목록 (드롭다운)
	    3. **경로 선택 섹션**: 3개 줄로 구성
	        - STORAGE 선택
	        - LIBRARY 선택/생성
	        - CELL 선택/생성
	    4. **하단 섹션**:  상태/오류 메시지 표시

*  주요 컴포넌트 상세: 
	 1. 상단 경로 표시/편집 필드, 확인/취소 버튼
		- 현재 선택된 workspace 경로를 "/user/{STORAGE}/VERIFY/SIGNOFF/{LIBRARY}/{CELL}/{USER}" 형식으로 실시간 표시
		- 직접 편집 가능한 텍스트 필드
		- 편집 및 업데이트 시 경로 유효성 자동 검사
		- 확인 버튼: 설정 완료 시 (기본적으로 비활성화, 유효한 workspace 경로 설정 시 활성화)
		- 취소 버튼: 설정 취소 시
	2. 최근 경로 섹션
		- `~/SOL/setting` JSON 파일에서 로드한 과거 workspace 목록
		- 드롭다운 형태로 제공
		- 선택 시 해당 경로를 상단 필드에 반영하고 각 선택 컴포넌트도 자동 업데이트
		- 목록 item제거 가능 
	 3. 경로 선택 섹션
		각 줄은 다음 요소로 구성:
		- 라벨 (STORAGE/LIBRARY/CELL)
		- 목록 표시 (리스트박스)
		- 새 항목 생성 컨트롤 (입력 필드 + 생성 버튼), 
		- 새 폴더 생성 시 775권한으로 생성되도록 만들어줘.
			**STORAGE 선택 줄**
			- 시스템 루트 디렉토리 목록 표시
			- 접근 권한에 따른 시각적 구분 (권한 없음: 회색/비활성화)
			- 선택 시 하위 LIBRARY 목록 자동 업데이트
			**LIBRARY 선택 줄**
			- 선택된 STORAGE 내 SIGNOFF 디렉토리의 하위 폴더 목록
			- 새 LIBRARY 생성 기능 (인라인 입력 필드 + 생성 버튼) 
			- 선택 시 하위 CELL 목록 자동 업데이트
			**CELL 선택 줄**
			- 선택된 LIBRARY 내 하위 폴더 목록
			- 새 CELL 생성 기능 (인라인 입력 필드 + 생성 버튼)
			- 선택 시 최종 workspace 경로 확정, 상단에 workspace 설정 표시 업데이트
	 4. 하단 섹션
		- 상태/오류 메시지 표시 영역: 권한 오류, 생성 실패 등 표시
* 경로 관리 및 탐색
	- **시스템 디렉토리 탐색**: ls 또는 glob 사용하여 디렉토리 내용 로드
	- **권한 검사**: 각 경로에 대한 읽기/쓰기 권한 확인 및 시각적 표시
	- **경로 저장**: 설정 완료된 workspace 경로를 JSON 파일에 저장
- LIBRARY 및 CELL 레벨에서 새 폴더 생성 지원
- 생성 전 이름 유효성 및 중복 검사
- 생성 실패 시 적절한 오류 메시지 표시
- 상단 경로 필드를 통한 직접 경로 편집 지원
- 편집된 경로 유효성 자동 검사
- 유효한 경로일 경우 각 선택 컴포넌트도 자동 업데이트
- 권한 없는 경로: 빨간색으로 하단에 "권한이 없습니다" 메시지 표시
- 새 폴더 생성 오류: 빨간색으로 하단에 오류 내용 표시
- 잘못된 경로 입력: 경로 유효성 검사 결과 즉시 표시
- 첫 실행 시 빈 값으로 시작
- 이전 설정 있을 경우 가장 최근 사용 workspace 자동 선택

- tkinter 라이브러리 사용
(파일 시스템 상호작용)
- 디렉토리 내용 로드: `os.listdir()` 또는 `glob.glob()`
- 권한 확인: `os.access(path, os.W_OK)`
- 새 디렉토리 생성: `os.makedirs()`
- JSON 파일 처리: `json.load()`, `json.dump()`
(사용자 경험 최적화)
- 목록 선택 시 즉시 다음 레벨 목록 업데이트
- 권한 없는 항목은 시각적으로 구분 (회색/비활성화)
- 현재 경로 실시간 업데이트
- 오류 메시지는 적절한 색상과 위치로 표시


</구현한 Sol Workspace 설정 기능들>


위와 같이 기술한 기능들을 잘 수행하는 sol_workspace_setup.py 가 잘 만들어졌고, 이를 배포해서 잘 사용하고 있어.

그런데 다음과 같이 signoff launcher workspace의 정책을 수정하고 그에 따라 sol_workspace_setup.py을 고쳐서 workspace를 설정하는 gui를 개선시키고 싶어.



변경 및 개선하고자 하는 내용들은 다음과 같아.


### 배경 설명:

* Cadence 사의 Virtuoso라는 schematic editor라는 Tool이 있는데, 이 툴에서는 나의 launcher와 같이 workspace를 지정하도록 하는 library manager라는 GUI가 있고, 사실 이를 참고해서 만든게 sol_workspace_setup.py야. 그런데 이 툴에서는 cds.lib라는 파일을 읽어서 선택할 library들과 cell들의 목록을 보여주고 관리하고있어.
* cds.lib의 구조는 다음과 같아: 
```

# 구조: DEFINE myDesign your_directory/myDesign
# 1. Open cds.lib and replace 'your directory' by your working directory as follows. (**Type the FULL directory name**)  
#    **DEFINE myDesign /home/grad/vanni/virtuoso/myDesign**
### HBM3E lib ###
DEFINE 20_HBM3E    /user/hbm28gvw00/DESIGN/SCHEM/20_HBM3E
DEFINE DRAMLIB    /user/dramrez/DRAMREZ/VSE/sdblib_vse/DRAMLIB
### HBM4 lib ###
DEFINE 00_HBM4_SCH_MAIN            /user/hbm28gvw00/DESIGN/SCHEM/00_HBM4_SCH_MAIN

### PERSONAL LIB ###

DEFINE WW       /user/deepwonwoo/VERIFY/SIGNOFF
```

* 그러면 DEFINE 이라고 시작하는 line을 parsing해서 DEFINE 다음에 오는 문자가 library가 되어서 library목록에 보여줘야 하는거고 그다음 경로에 있는 디렉토리에 있는 모든 폴더들이 cell이고 이를  cell 목록에 보여줘야해.

	예를 들어 library manager에서 library에는 20_HBM3E,  DRAMLIB, 00_HBM4_SCH_MAIN, WW 가 목록에 뜰테고, 만약 WW를 선택하게 된다면  /user/deepwonwoo/VERIFY/SIGNOFF에 있는 모든 폴더목록들을 cell list에 보여줘서 선택하게 하여 해당 cell 경로까지를 workspace 경로를 설정하게 하고있어.

* 이런 cds.lib 파일들은 모두 가각의 Storage 프로젝트 계정의 다음과 같은 경로에 있어. 
	  cds.lib 위치 : /user/{Stoage}/SCHEM/cds.lib


### 추가 구현 및 개선하고자 부분:


*  `ls /user/*` 에서 접근이 확인되는 연결된 storage project 계정들을 상단의 드롭다운을 통해 목록을 보여주고 권한이 있는 계정 경로에 대해서는 선택 가능하게 만듬.'
  (workspace path와 recent path Interface는 여전히 존재! 그 밑에 GUI적으로 잘 만들어서 PROJECT선택하게 만듬)
*    선택한 계정을 바탕으로 cds.lib을 찾아서 library목록들을 가져옴.
	  * 이때 선택한 계정 이름 뒤에 숫자가 있다면 추가적으로 숫자부분을 00으로 바꾸고 그곳의 계정경로의 cds.lib에 대해서도 처리해야함. 예를 들어 만약 계정 선택을 hbm28gvw20 을 선택했다면 /user/hbm28gvw20/SCHEM/cds.lib 뿐만 아니라 /user/hbm28gvw00/SCHEM/cds.lib 도 추가적으로 parsing해야함.
	  * library가 중복된다면 하나로 합쳐야함. 예를 들어 /user/hbm28gvw20/SCHEM/cds.lib파일에는 "DEFINE HBM_MAIN  /user/l48hbm/DESIGN/SCHEM/HBM1"으로 작성 되어있고 /user/hbm28gvw00/SCHEM/cds.lib파일에는  "DEFINE HBM_MAIN  /user/l00hbm/DESIGN/SCHEM/HBM00"으로 작성 되어 있다면 HBM_MAIN 이라는 HBM_MAIN를 선택할때는 /user/l48hbm/DESIGN/SCHEM/HBM1 와 /user/l00hbm/DESIGN/SCHEM/HBM00 에 있는 폴더들을 cell list로 보여줘야해.
	  
* 지금의 workspace_setup.py는 맨 왼쪽 줄에서는 storage 선택, 가운데는줄에서는 library선택, 오른쪽 줄에서는 Cell을 선택하게 목록들이 보였는데,  개선된 버전에서는 Storage Project 계정을 위로 빼서 드롭다운 형식으로 구현하였기에 VSE의 Library Manager GUI와 같이 맨 왼쪽의 list에서는 library, 가운데는 cell, 오른쪽 라인에서는 User Directory(VSE에서는 View)를 선택하게끔 만들어줘.
* 만약 내가 선택한 계정에 SCHEM/cds.lib 파일이 없다면 기존의 기능도 잘 동작할수있도록 /user/{storage}/VERIFY/SIGNOFF/{LIB}/{CELL}/{USERNAME} 의 workspace 경로 설정 기능도 잘 동작될수있도록 만들어줘.
*  workspace 경로를 꼭 표준으로 정한  `/user/{STORAGE}/VERIFY/SIGNOFF/{LIBRARY}/{CELL}/{USER}` 형태를 따르는게 아니라, 새로운 표준 경로로 Virtuoso의 cds.lib을 통해 설정한 경로로도 workspace가 설정될수있도록 만들고 싶어.
