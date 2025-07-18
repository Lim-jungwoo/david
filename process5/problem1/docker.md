# 컨테이너 관련 개념 정리

## 1. 가상머신(Virtual Machine)과 컨테이너(Container)의 차이

| 항목        | 가상머신(VM)                               | 컨테이너(Container)                                      |
| ----------- | ------------------------------------------ | -------------------------------------------------------- |
| 구조        | 하이퍼바이저 위에 게스트 OS 포함           | 호스트 OS 위에서 애플리케이션과 필요한 라이브러리만 실행 |
| 부팅 시간   | 수 분                                      | 수 초                                                    |
| 자원 사용량 | 무겁고 리소스를 많이 사용                  | 가볍고 리소스를 적게 사용                                |
| 격리 수준   | 커널 포함 전체 OS 수준 격리                | 프로세스 수준 격리 (공유 커널)                           |
| 운영체제    | 다양한 OS 가능 (예: Linux 위에 Windows VM) | 커널 공유로 동일한 OS 커널 기반                          |

컨테이너는 VM보다 경량이며, 빠르게 실행되고, 자원을 효율적으로 사용합니다. 반면, 보안 격리나 완전한 OS 환경이 필요한 경우 VM이 적합합니다.

---

## 2. 컨테이너(Container)와 이미지(Image)의 차이

| 항목      | 이미지(Image)                        | 컨테이너(Container)         |
| --------- | ------------------------------------ | --------------------------- |
| 정의      | 실행 가능한 컨테이너의 정적인 설계도 | 실행 중인 이미지의 인스턴스 |
| 상태      | 불변 (Immutable)                     | 가변 (변화 가능)            |
| 실행 여부 | 실행되지 않음                        | 실행 중인 프로세스          |
| 생성 방법 | Dockerfile로 생성                    | 이미지에서 생성하여 실행    |

이미지는 일종의 템플릿이며, 컨테이너는 해당 이미지를 바탕으로 실행된 실체입니다.

---

## 3. 컨테이너 런타임(Container Runtime) 정의

**컨테이너 런타임**은 컨테이너를 생성, 실행, 관리하는 소프트웨어입니다. 주요 기능은 다음과 같습니다:

- 컨테이너 이미지 풀링(pull)
- 컨테이너 생성 및 실행
- 프로세스 격리 및 네트워크 설정
- 리소스 제어(CPU, 메모리 제한)

Docker도 컨테이너 런타임을 포함하고 있으며, 그 내부적으로는 `containerd`, `runc`와 같은 런타임을 사용합니다.

---

## 4. CNCF Landscape 기반 컨테이너 런타임 종류 (3가지)

CNCF(Cloud Native Computing Foundation) Landscape에 따르면, 주요 컨테이너 런타임은 다음과 같습니다:

---

### 1. runc

- **정의**: OCI(Open Container Initiative) 런타임 스펙을 구현한 **최하위 컨테이너 실행 도구**
- **역할**: 컨테이너를 실제로 **시작/중지/삭제**하는 작업 수행
- **특징**:
  - 경량화된 CLI 기반 실행기
  - containerd, CRI-O가 내부적으로 호출
  - 독립 실행도 가능하지만 일반적으로 상위 런타임에 의해 사용됨

---

### 2. containerd

- **정의**: Docker에서 파생되어 CNCF로 기여된 **범용 컨테이너 런타임**
- **역할**:
  - **이미지 관리, 네트워크, 스냅샷**, 컨테이너 실행 등 전체 수명 주기 관리
  - 내부적으로 runc를 호출하여 실제 컨테이너 실행
- **특징**:
  - Docker의 핵심 구성 요소였음
  - Kubernetes에서는 CRI plugin을 통해 사용 가능
  - AWS EKS, Rancher 등에서 널리 채택

---

### 3. CRI-O

- **정의**: Kubernetes만을 위한 **경량화된 컨테이너 런타임**
- **역할**:
  - Kubernetes의 kubelet과 직접 통신하는 CRI(Container Runtime Interface) 구현체
  - 내부적으로 runc를 사용하여 컨테이너 실행
- **특징**:
  - Kubernetes 외 다른 목적은 배제
  - 보안 기능 강화 (SELinux, seccomp, AppArmor 등)
  - Red Hat OpenShift의 기본 런타임

---

## 📊 요약 비교표

| 항목            | runc                        | containerd                                     | CRI-O                                     |
| --------------- | --------------------------- | ---------------------------------------------- | ----------------------------------------- |
| 유형            | Low-level Runtime           | High-level Runtime                             | Kubernetes 전용 Runtime                   |
| Kubernetes 연동 | ❌ 직접 사용 불가           | ✅ CRI plugin 사용                             | ✅ CRI 직접 구현                          |
| 주요 기능       | 컨테이너 실행               | 이미지 관리, 네트워크, 볼륨, 실행 등 전체 관리 | Kubernetes에 최적화된 컨테이너 실행       |
| 주요 사용자     | containerd, CRI-O 내부 모듈 | Docker, Kubernetes, EKS 등                     | OpenShift, Red Hat 기반 Kubernetes 배포판 |
| 보안 기능       | 기본 Linux 기능             | 기본 제공                                      | 강화된 보안 (SELinux, seccomp 등)         |

---

## 5. 도커 이미지의 레이어(Image Layer)

Docker 이미지의 레이어 구조는 다음과 같은 특징을 가집니다:

- 이미지 = 여러 레이어(layer)의 **합성 결과**
- 각 레이어는 Dockerfile의 명령어(`RUN`, `COPY`, `ADD` 등) 한 줄마다 생성됨
- 레이어는 **캐시**로 활용되어 빌드 속도 향상
- 변경된 레이어만 다시 생성되므로 효율적
- 최상위 레이어는 **읽기-쓰기** (container layer), 하위 레이어는 읽기 전용

### 예시

```dockerfile
FROM ubuntu
RUN apt-get update
RUN apt-get install -y python3
COPY . /app
```
