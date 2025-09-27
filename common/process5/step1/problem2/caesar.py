import string

def caesar_cipher_decode(target_text: str):
    """
    카이사르 암호를 자리수(시프트) 별로 해독하는 함수
    - target_text: 암호화된 문자열
    - 소문자, 대문자 모두 변환
    - 숫자, 공백, 특수문자는 그대로 둠
    """
    results = []
    lower = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
    upper = string.ascii_uppercase  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for shift in range(1, 26):  # 1~25까지 시프트
        decoded = []
        for ch in target_text:
            if ch.islower():
                idx = (lower.index(ch) - shift) % 26
                decoded.append(lower[idx])
            elif ch.isupper():
                idx = (upper.index(ch) - shift) % 26
                decoded.append(upper[idx])
            else:
                decoded.append(ch)
        decoded_text = ''.join(decoded)
        results.append((shift, decoded_text))
        print(f"[{shift}] {decoded_text}")  # 콘솔 출력
    
    return results


if __name__ == "__main__":
    # 1. password.txt 읽기
    with open("password.txt", "r", encoding="utf-8") as f:
        encrypted_text = f.read().strip()

    # 2. 모든 shift 결과 출력
    results = caesar_cipher_decode(encrypted_text)

    # 3. 사람이 보고 맞는 shift 선택
    choice = int(input("\n정답으로 보이는 shift 값을 입력하세요 (1~25): "))

    # 4. 선택한 결과 result.txt에 저장
    with open("result.txt", "w", encoding="utf-8") as f:
        f.write(results[choice - 1][1])

    print("\nresult.txt 파일에 저장 완료")
