# Personal Access Token을 텍스트 파일로 저장한 뒤 삭제해야 하는 이유

## 🔐 Personal Access Token(PAT)이란?

- GitHub에서 사용자 인증을 위해 사용하는 **비밀번호 대체 문자열**
- 주로 `git push`, API 호출, CI/CD 자동화 등에 사용됨
- 사용자의 GitHub 계정 권한을 거의 그대로 가지므로, 유출 시 매우 위험함

---

## ⚠️ 텍스트 파일에 저장 후 삭제해야 하는 이유

### 1. 평문 저장은 보안 위험이 높음

- `.txt` 파일은 암호화되지 않은 **평문(Plain Text)** 이므로 누구나 열람 가능
- 로컬에 저장된 상태에서 **무심코 공유, 백업, 커밋**될 위험 존재

### 2. 실수로 Git에 커밋 가능

- `token.txt` 파일을 `.gitignore`에 추가하지 않으면 Git에 커밋되어 외부에 유출될 수 있음
- GitHub는 코드 내에 토큰이 포함되면 **자동으로 해당 토큰을 비활성화 처리함**

### 3. 클라우드/공용 컴퓨터 환경에서는 더 위험

- 토큰 파일이 클라우드 동기화(Google Drive, Dropbox 등)되거나
- 공용 PC에서 남아 있을 경우 **다른 사용자가 접근할 수 있음**

### 4. 삭제하지 않으면 장기적으로 관리가 어려움

- 시간이 지나면서 어떤 토큰이 어디서 쓰였는지 추적하기 어려워짐
- 오래된 토큰이 유출되어도 인지하기 어려움

---

## ✅ 안전하게 토큰 사용하는 방법

| 방법                               | 설명                                                    |
| ---------------------------------- | ------------------------------------------------------- |
| 환경변수로만 사용                  | `.bashrc`, `.zshrc` 등에 `export GITHUB_TOKEN=...` 설정 |
| 운영체제 자격 증명 저장소 사용     | macOS: 키체인, Windows: 자격 증명 관리자                |
| `.gitignore`에 민감 정보 포함      | `.env`, `token.txt` 등 커밋 제외                        |
| 필요시만 파일에 저장하고 즉시 삭제 | 한 번 사용 후 `rm token.txt` 실행                       |

---

## 📌 결론

**Personal Access Token은 비밀번호와 같은 민감한 자격 증명입니다.**  
임시로 파일에 저장해야 할 경우에도 **즉시 삭제**하여 보안 사고를 예방해야 합니다.

```bash
# 사용 예시
cat token.txt | pbcopy  # 토큰을 클립보드에 복사
rm token.txt            # 즉시 파일 삭제
```
