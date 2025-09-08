# 시그모이드(Sigmoid) 함수 정리

## 정의

시그모이드(sigmoid) 함수는 **입력값을 0과 1 사이로 압축하는 S자 형태의 함수**입니다.

$$
\sigma(x) = \frac{1}{1 + e^{-x}}
$$

---

## 특징

1. **출력 범위**

   - 모든 실수 입력값을 0과 1 사이 값으로 변환
   - $x \to -\infty$ 일 때 $\sigma(x) \to 0$
   - $x \to +\infty$ 일 때 $\sigma(x) \to 1$

2. **미분**

   - 도함수(derivative)는 아래와 같이 간단합니다.

     $$
     \sigma'(x) = \sigma(x)\bigl(1 - \sigma(x)\bigr)
     $$

3. **성질**
   - $\sigma(0) = 0.5$
   - 작은 입력은 0 근처, 큰 입력은 1 근처로 포화(saturation)
   - 극단 구간에서는 기울기가 작아져 **기울기 소실(vanishing gradient)** 이 발생할 수 있음

---

## 활용

- **로지스틱 회귀(Logistic Regression)**: 사건이 발생할 **확률**을 출력
- **신경망(Neural Network)**: 활성화 함수로 사용 (현재는 ReLU, *Rectified Linear Unit*가 더 보편적)
- **이진 분류(Binary Classification)**: 출력층에서 확률 모델링

---

## 렌더링 팁

- 이 파일은 수식에 **$...$**(인라인), **$$...$$**(블록) 표기를 사용했습니다.
- GitHub, Obsidian, VS Code의 일부 확장 등 **MathJax/KaTeX** 를 지원하는 뷰어에서 올바르게 렌더링됩니다.
- Jekyll(예: GitHub Pages) 테마를 쓰는 경우, MathJax/KaTeX 활성화 설정이 필요할 수 있습니다.

---

**한 줄 요약**  
시그모이드 함수는 임의의 입력값을 **확률처럼 0과 1 사이**로 변환하는 함수입니다.
