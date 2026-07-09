---
layout: post
title: "GitHub SSH 키 설정 가이드:비밀번호 없이 안전하게 Git 사용하기"
date: 2025-08-12T10:28:06.488Z
categories:
  - DevOps
---

## 1. SSH 키란 무엇인가?
기존에 **HTTPS 경로**로 원격 저장소 URL을 저장하면, 매번 **ID·비밀번호 또는 인증 토큰**을 입력해야 했습니다.
하지만 **SSH 키**를 사용하면 비밀번호 노출 위험이 줄고, 한 번 설정 후에는 매번 입력할 필요가 없습니다.
또한** CI/CD 자동화 환경**에서도 안전하게 인증을 처리할 수 있습니다.

---

## 2. HTTPS vs SSH 방식 비교
| 구분     | HTTPS         | SSH               |
| ------ | ------------- | ----------------- |
| 인증 방식  | ID·비밀번호 또는 토큰 | SSH 키             |
| 사용 편의성 | 매번 입력 필요      | 한 번 설정하면 이후 자동 인증 |
| 보안성    | 토큰 노출 위험 존재   | 개인 키 보관 시 안전      |

---
## 3.SSH 키 생성하기

터미널(또는 Git Bash)에서 다음 명령어를 입력합니다.

``` bash
ssh-keygen -t ed25519 -C "your_email@example.com"
{% highlight text %}
- `t ed25519` → 최신 권장 알고리즘 (RSA보다 보안성·속도 우수)

- `C` → 키에 대한 설명(주석), 주로 이메일 주소 사용

📌 **RSA 대신 ED25519를 권장하는 이유**

- 더 짧은 키 길이로도 높은 보안성
- 키 생성 및 인증 속도 빠름
- 파일 크기 작아 관리 효율적
- 단, 오래된 서버는 RSA만 지원할 수 있음

---
**키 생성 화면 예시**
![](https://velog.velcdn.com/images/duwnstj12/post/9218324a-b212-44f6-be20-550d74f522f0/image.png)
> 키 생성이 끝나면 .ssh 폴더로 이동해 확인합니다.
Windows 기준, 경로는 C:\Users\<사용자명>\.ssh 입니다.

---
**키파일 예시**
![](https://velog.velcdn.com/images/duwnstj12/post/51450019-e7be-4423-a94f-067e672e87e0/image.png)
- `id_ed25519` → 개인 키 **(절대 외부 노출 금지)**

- `id_ed25519.pub` → 공개 키 (GitHub 등록용)
---
## GitHub에 SSH 공개 키 등록하기
1. **GitHub → Settings → SSH and GPG keys**로 이동

2. **New SSH key** 클릭

3. **Title:** 원하는 이름 입력

4. **Key:** .pub 파일 내용 복사 후 붙여넣기

{% endhighlight %} bash
cat ~/.ssh/id_ed25519.pub
{% highlight text %}
cat 명령어는 리눅스 명령어로 **해당 파일을 출력**해준다.

5. **Key type**: Authentication Key 선택
6. 저장하면 완료 🎉
---


## 5. 기존 프로젝트 원격 저장소 URL을 SSH로 변경하기
현재 원격 저장소 주소 확인:
{% endhighlight %} bash
git remote -v
{% highlight text %}
![](https://velog.velcdn.com/images/duwnstj12/post/f23061c4-0e1e-4a08-b738-e4e50fd13217/image.png)

---
Github에서 SSH 주소 복사 : 
![](https://velog.velcdn.com/images/duwnstj12/post/64f1721d-8247-4a9c-841b-8219d7243c06/image.png)

---
원격 저장소 주소 변경:
{% endhighlight %} bash
git remote set-url origin git@github.com:username/repository.git

{% highlight text %}
---


## 6. 설정 확인 및 테스트 방법


![](https://velog.velcdn.com/images/duwnstj12/post/8bdd1141-a0c3-4cc0-89ce-e6cfccdf86e9/image.png)

SSH 연결 테스트:

{% endhighlight %} bash
ssh -T git@github.com
{% highlight text %}
성공 시: 

{% endhighlight %} bash
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```
---
## 7. SSH 사용의 장점
- **비밀번호 입력 불필요** → 작업 속도 향상

- **보안성 강화** → 개인 키 유출만 방지하면 안전

- **자동화에 적합** → CI/CD 환경에서 인증 자동 처리 가능
---

## 자주 발생하는 오류와 해결 방법
| 오류 메시지                                | 원인               | 해결 방법                                          |
| ------------------------------------- | ---------------- | ---------------------------------------------- |
| Permission denied (publickey)         | 키 미등록/경로 오류      | `ssh-add ~/.ssh/id_ed25519` 실행                 |
| Host key verification failed          | GitHub 호스트 인증 실패 | `ssh-keyscan github.com >> ~/.ssh/known_hosts` |
| Could not resolve hostname github.com | 네트워크/방화벽 문제      | 인터넷 연결·VPN 설정 확인                               |

---

## 마무리 및 보안 팁
- **⚠️ 절대 개인 키는 외부에 노출하지 마세요**
- 중요 서비스에는 **별도의 SSH 키** 사용 권장
- 키는 **주기적으로 재발급 및 관리**

- 오래된 서버 연결 시 RSA(4096비트) 사용 고려