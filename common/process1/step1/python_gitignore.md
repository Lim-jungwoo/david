# Python 및 Flask 프로젝트에서 .gitignore 설정 가이드

---

## 1. `__pycache__`와 `.venv` 디렉토리의 생성 이유 및 `.gitignore`에 추가해야 하는 이유

### 📁 `__pycache__/`

- **생성 이유**: Python은 `.py` 파일을 실행할 때 내부적으로 바이트코드(`.pyc`)로 변환하여 `__pycache__` 디렉토리에 저장함.
- **장점**: 실행 속도 향상 (재컴파일 방지)
- **.gitignore에 추가해야 하는 이유**:
  - 프로젝트 실행에 필수적이지 않음 (자동 생성됨)
  - 플랫폼 및 Python 버전에 따라 내용이 달라질 수 있음
  - Git 저장소의 불필요한 용량 증가를 방지

### 📁 `.venv/`

- **생성 이유**: Python 가상환경. 프로젝트별 독립적인 패키지 설치 및 관리 목적
- **장점**: 패키지 버전 충돌 방지, 프로젝트 간 환경 격리
- **.gitignore에 추가해야 하는 이유**:
  - 환경마다 디렉토리 내용이 다르며, 경로도 시스템마다 다름
  - 용량이 크고 Git 저장소에 불필요
  - 가상환경은 `requirements.txt` 또는 `pyproject.toml`로 재구성 가능

---

## 2. GitHub의 `.gitignore` 템플릿(Python)을 선택했을 때 포함되는 주요 항목

> 출처: [GitHub/gitignore - Python Template](https://github.com/github/gitignore/blob/main/Python.gitignore)

### 🧹 주요 포함 항목

| 범주           | 예시 항목                                              |
| -------------- | ------------------------------------------------------ |
| ✅ Python 캐시 | `__pycache__/`, `*.py[cod]`, `*$py.class`              |
| ✅ 가상환경    | `.venv/`, `env/`, `ENV/`                               |
| ✅ 배포 빌드   | `build/`, `dist/`, `*.egg-info/`, `MANIFEST`           |
| ✅ 테스트 결과 | `.coverage`, `.pytest_cache/`, `htmlcov/`, `.tox/`     |
| ✅ 환경변수    | `.env`, `.env.*`                                       |
| ✅ IDE/편집기  | `.vscode/`, `.idea/`, `.spyderproject`, `.ropeproject` |
| ✅ 문서 생성   | `docs/_build/`, `/site`                                |
| ✅ Jupyter     | `.ipynb_checkpoints/`                                  |
| ✅ 타입 검사   | `.mypy_cache/`, `.pytype/`, `.pyre/`                   |

---

## 3. Flask 기반 프로젝트에서 `.gitignore`에 추가해야 하는 항목

### 📦 기본적으로 포함할 항목

```gitignore
# Python 캐시
__pycache__/
*.py[cod]
*.pyo

# 가상환경
.venv/
venv/
ENV/
env/

# 환경변수 및 민감정보
.env
.env.*

# Flask 인스턴스 관련
instance/
.webassets-cache

# 데이터베이스 (sqlite 등)
*.db
*.sqlite3

# 로그 파일
*.log

# IDE 설정
.vscode/
.idea/

# 테스트 및 커버리지
.pytest_cache/
.coverage
htmlcov/
```
