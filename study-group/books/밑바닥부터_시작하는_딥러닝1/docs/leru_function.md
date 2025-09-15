# ReLU(Rectified Linear Unit) 함수 정리

## 📌 정의

**ReLU(Rectified Linear Unit, 정류 선형 유닛)** 는 입력값이 **양수면 그대로 통과**, **음수면 0으로 잘라내는** 비선형 활성화 함수입니다.  
심층 신경망의 은닉층에서 가장 널리 쓰이는 기본 선택지입니다.

$$
\mathrm{ReLU}(x) = \max(0, x)
$$

---

## 📌 미분(Gradient)

ReLU의 도함수(gradient)는 다음과 같습니다.

$$
\frac{d}{dx}\,\mathrm{ReLU}(x) =
\begin{cases}
0, & x < 0 \\
1, & x > 0 \\
\text{정의 불가(보통 0 또는 1로 둠)}, & x = 0
\end{cases}
$$

실무에서는 \(x=0\)에서의 기울기를 **0**으로 두는 경우가 일반적입니다.

---

## 📌 특징

- **비포화(non-saturating)**: \(x>0\)에서 기울기 1 → 기울기 소실(vanishing gradient) 완화
- **희소성(sparsity)**: $x \le 0$에서 출력 0 → 표현이 희소해져 연산 효율 및 일반화 기여
- **계산 효율성(computation efficiency)**: $\max(0,x)$만 계산 → GPU 병렬화에 유리
- **비선형성(non-linearity)**: 여러 층을 쌓아 복잡한 패턴을 모델링 가능

---

## 📌 단점 및 보완

- **다잉 ReLU(Dying ReLU)**: 일부 뉴런이 항상 0 출력 → 학습 중단
- **0에서 비미분**: 수학적으로는 미분 불가 → 프레임워크에서 보통 0 처리

보완 방법:

- **Leaky ReLU**: $f(x)=\max(\alpha x, x),\quad 0<\alpha\ll 1$
- **PReLU**: $\alpha$를 학습 파라미터로 확장
- **ELU, GELU, Swish** 등 대체 함수 사용
- **He 초기화 + Batch Normalization**으로 학습 안정성 확보

---

## 📌 코드 예시

### Python (NumPy)

```python
import numpy as np

def relu(x):
    return np.maximum(0, x)

def relu_grad(x):
    grad = np.zeros_like(x, dtype=float)
    grad[x > 0] = 1.0
    return grad

x = np.array([-2.0, -0.1, 0.0, 0.3, 5.0])
print("ReLU(x):", relu(x))
print("ReLU'(x):", relu_grad(x))
```
