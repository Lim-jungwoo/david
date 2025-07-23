# 🐳 DockerHub를 사용하는 이유

## 📌 DockerHub란?

DockerHub는 Docker 이미지의 저장, 공유, 배포를 위한 **공식 Docker 이미지 저장소(Registry)**입니다. GitHub가 코드 저장소라면, DockerHub는 **컨테이너 이미지 저장소**입니다.

---

## ✅ 사용하는 이유

### 1. **이미지의 중앙 저장소 역할**

- 애플리케이션을 Docker 이미지로 만들어 **클라우드에 저장** 가능
- 개발자 또는 팀원이 **언제 어디서든 pull** 하여 동일한 환경에서 실행 가능

### 2. **이미지 공유 및 협업**

- 공개 저장소(Public Repository)를 통해 전 세계에 공유 가능
- 비공개 저장소(Private Repository)로 팀 내 보안 협업도 가능

### 3. **CI/CD 파이프라인 통합**

- GitHub Actions, GitLab CI 등과 연동하여 자동으로 이미지를 build & push
- 버전별 태그(tag)를 통해 배포 이미지 관리

### 4. **Docker 공식 이미지 제공**

- Ubuntu, Nginx, Redis, Node.js 등 수많은 **공식 이미지** 제공
- 신뢰할 수 있는 이미지 기반으로 빠른 개발 가능

### 5. **버전 관리 및 태깅**

- `v1.0`, `latest` 같은 **태그(Tag)** 를 붙여 버전 관리 가능
- 특정 시점의 이미지로 정확하게 롤백/테스트 가능

---

## 📦 예시 사용 흐름

```bash
# 이미지 빌드
docker build -t myapp .

# 태그 추가
docker tag myapp docker.io/username/myapp:v1.0

# DockerHub에 Push
docker push docker.io/username/myapp:v1.0
```
