# 🐳 Windows Docker Desktop: Linux 컨테이너 vs Windows 컨테이너

Docker Desktop은 Windows에서 **Linux 컨테이너**와 **Windows 컨테이너**를 모두 실행할 수 있도록 지원한다. 이 문서는 두 컨테이너의 차이점과 각각의 특징을 정리한다.

---

## ✅ 1. 실행 방식

| 항목      | Linux 컨테이너                     | Windows 컨테이너              |
| --------- | ---------------------------------- | ----------------------------- |
| 실행 기반 | WSL 2 또는 Hyper-V 기반의 Linux VM | Windows 커널 및 Windows OS    |
| 커널 공유 | Linux 커널 (가상화 기반)           | Windows 커널                  |
| 호환성    | 리눅스용 바이너리만 실행 가능      | 윈도우용 바이너리만 실행 가능 |

---

## ✅ 2. 이미지 및 호환성

| 항목                  | Linux 컨테이너                           | Windows 컨테이너                          |
| --------------------- | ---------------------------------------- | ----------------------------------------- |
| 이미지 유형           | `python:3`, `ubuntu`, `nginx` 등         | `mcr.microsoft.com/windows/servercore` 등 |
| 크로스 플랫폼         | ❌ (Windows에서 직접 실행 불가, VM 기반) | ❌ (Windows 컨테이너는 Windows OS 전용)   |
| 사용 가능한 이미지 수 | 방대함 (Docker Hub의 대다수)             | 제한적 (Windows 전용 이미지에 한정됨)     |

---

## ✅ 3. 성능 및 사용성

| 항목                | Linux 컨테이너 | Windows 컨테이너                           |
| ------------------- | -------------- | ------------------------------------------ |
| 부팅 속도           | 빠름 (경량)    | 느림 (무거운 OS)                           |
| 자원 사용           | 적음           | 많음                                       |
| Docker Compose 지원 | 완벽 지원      | 제한적 지원 또는 별도 설정 필요            |
| 다중 플랫폼 개발    | 적합           | 제한적 (Windows 전용 환경에서만 사용 권장) |

---

## ✅ 4. 파일 시스템과 호환성

| 항목                     | Linux 컨테이너                        | Windows 컨테이너                         |
| ------------------------ | ------------------------------------- | ---------------------------------------- |
| 호스트와 파일 공유       | WSL2 기반 파일 시스템과 연동          | NTFS 기반                                |
| 경로 호환성              | `/app`, `/usr/src` 등 Linux 경로 사용 | `C:\app`, `D:\data` 등 Windows 경로 사용 |
| 줄바꿈 문제 (CRLF vs LF) | 주의 필요                             | 기본적으로 CRLF 사용                     |

---

## ✅ 5. 전환 방법

```bash
# PowerShell에서 컨테이너 유형 전환
# Linux → Windows 컨테이너로 전환
& 'C:\Program Files\Docker\Docker\DockerCli.exe' -SwitchDaemon

# 또는 Docker Desktop UI → "Switch to Windows containers"
```
