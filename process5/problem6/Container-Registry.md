# 📦 대표적인 Container Registry 3가지

컨테이너 레지스트리(Container Registry)는 컨테이너 이미지를 저장, 관리, 배포할 수 있는 저장소입니다. 다음은 널리 사용되는 3가지 Container Registry입니다.

---

## 1. 🐳 DockerHub

### ✅ 개요

- Docker의 공식 이미지 저장소
- Public 및 Private 저장소 지원

### ✅ 특징

- 가장 널리 사용됨 (기본 Docker CLI 설정 대상)
- 공식 이미지(Official Image) 다수 존재
- CI/CD 연동과 자동 빌드 기능 지원
- 무료 계정은 Private 저장소 제한 있음

### ✅ URL

- https://hub.docker.com

---

## 2. ☁️ Amazon Elastic Container Registry (ECR)

### ✅ 개요

- AWS에서 제공하는 고성능 Container Registry
- AWS IAM과 통합된 보안 정책 제공

### ✅ 특징

- Amazon ECS, EKS와 자연스럽게 통합
- 이미지 스캔 및 취약점 진단 기능 제공
- 퍼블릭 및 프라이빗 저장소 모두 지원
- 가격은 저장 용량과 데이터 전송량 기준 과금

### ✅ URL

- https://aws.amazon.com/ecr/

---

## 3. 🧭 GitHub Container Registry (GHCR)

### ✅ 개요

- GitHub Packages의 일부로 제공되는 Container Registry
- GitHub Actions와 밀접한 통합

### ✅ 특징

- GitHub 리포지토리와 바로 연동 가능
- 저장소 단위 접근 제어 및 조직 정책 설정 용이
- `ghcr.io/<username>/<image>` 형식으로 사용

### ✅ URL

- https://github.com/features/packages

---

## 📝 비교 요약

| 항목          | DockerHub      | Amazon ECR       | GitHub Container Registry |
| ------------- | -------------- | ---------------- | ------------------------- |
| 제공 업체     | Docker         | AWS              | GitHub (Microsoft)        |
| 퍼블릭 지원   | ✅ 있음        | ✅ 있음          | ✅ 있음                   |
| 프라이빗 지원 | ✅ 있음        | ✅ 있음          | ✅ 있음                   |
| 접근 제어     | 기본 인증/토큰 | IAM 기반         | GitHub 권한 기반          |
| 통합 대상     | 모든 플랫폼    | AWS ECS, EKS 등  | GitHub Actions            |
| 과금 방식     | 무료/유료 혼합 | 저장/전송량 기반 | GitHub 저장소 기준        |

---

## 🏁 결론

각 Container Registry는 개발 환경과 배포 전략에 따라 선택할 수 있으며,

- 빠르게 시작하고 싶다면 **DockerHub**
- AWS 인프라를 활용한다면 **Amazon ECR**
- GitHub 중심의 CI/CD를 원한다면 **GitHub Container Registry**가 적합합니다.
