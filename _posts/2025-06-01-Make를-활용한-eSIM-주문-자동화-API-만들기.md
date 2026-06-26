---
layout: post
title: "📦 Make를 활용한 eSIM 주문 자동화 API 만들기 "
date: 2025-06-01T12:23:40.401Z
---

# 🧩 목표 : Make로 스마트스토어 esim 주문 자동화 시스템 만들기
> 코딩 없이 `Make`를 활용하여 스마트스토어 주문을 자동 처리하는 eSIM 주문 시스템을 구축해보았다. 스마트스토어 주문 메일을 기반으로 고객 정보를 파싱하고, GoogleSheets에 저장하여 외부 API로 esim을 발급하는 전체 자동화 과정을 소개한다.

### 전체 구조
1. 스마트스토어 주문 수신 →
메일로 주문 정보 도착 (네이버 메일 사용)

2. 메일 내용 파싱 →
필요한 정보 추출 (고객명, 전화번호 등)

3. 구글 시트에 저장 →
고객 정보를 저장해 DB처럼 활용

4. API로 주문 요청 전송 →
외부 공급사의 eSIM 발급 API에 정보 전달

5. 고객에게 결과 발송 →
이메일 또는 카카오톡으로 eSIM 정보 전달


## 네이버 IMAP 설정
### IMAP란?
메일을 외부 시스템에서 자동으로 **수신·처리**할 수 있도록 해주는 표준 프로토콜이다.
### 네이버 IMAP 활성화
1. [네이버 메일 환경설정](https://mail.naver.com) -> POP3/IMAP설정
2. IMAP 사용설정을 **사용함**으로 변경
![](https://velog.velcdn.com/images/duwnstj12/post/32ff8aa8-0260-4fe0-b940-78f6cadc2776/image.png)
![](https://velog.velcdn.com/images/duwnstj12/post/21962b10-15de-44ea-85b9-3b771000fbaf/image.png)

### 앱 비밀번호 발급
보안을 위해 IMAP 접속에는 일반 비밀번호 대신 **앱 전용 비밀번호**를 사용해야한다.

1. 네이버 > **보안설정** 이동
2. 2단계 인증 설정
3. 앱 비밀번호 생성
![](https://velog.velcdn.com/images/duwnstj12/post/adf57b24-db96-45fc-b214-22fc470584f3/image.png)
![](https://velog.velcdn.com/images/duwnstj12/post/1b7b77cd-01af-41c4-a252-560ddcac5564/image.png)
![](https://velog.velcdn.com/images/duwnstj12/post/5added32-1ac1-458d-a9ea-d473eacc152b/image.png)

## Make에서 IMAP 모듈 연결하기
Make에서 메일을 수신하기 위한 **IMAP 모듈 설정을 진행한다.

- **서버 주소(IMAP Server)**: imap.naver.com

- **포트 번호(Port)**: 993

- **사용자 이름(Username)**: 네이버 ID

- **앱 비밀 번호(Password)**: 생성한 앱 비밀번호 입력

![](https://velog.velcdn.com/images/duwnstj12/post/527f2bdb-64dd-4c84-a65b-79569128e627/image.png)
> 설정 후 `Save`하면 IMAP 메일 수신 모듈이 추가된다.

## 이메일 필터 설정
- **Folder**: `/INBOX(받은 메일함)`

- **Criteria**: 제목에 `주문` 포함된 메일만 수신

![](https://velog.velcdn.com/images/duwnstj12/post/b85d69e5-5081-421c-bf7e-e8945da97cfe/image.png)

## 메일 파싱 - TextParser 설정
메일 본문에서 고객 정보를 추출하려면, HTML ->TEXT 변환후 정규식을 적용한다.

## HTML to Text 모듈 추가
IMAP로 받은 HTML 본문을 `plain text`로 변환해야 정확하게 파싱된다.

### 정규식 패턴 예시
```java
고객명[:：]?\s*(.*?)\s*
전화번호[:：]?\s*(.*?)\s*
이메일[:：]?\s*(.*?)\s*
상품명[:：]?\s*(.*?)\s*
수량[:：]?\s*(.*?)\s*
요청사항[:：]?\s*(.*)
```

## 정규식 설명
| 항목         | 설명                  |
| ---------- | ------------------- |
| `고객명[:：]?` | `고객명:` 또는 `고객명：` 인식 |
| `\s*`      | 공백 문자 제거            |
| `(.*?)`    | 실제 값 추출 (캡처 그룹)     |
| `.*`       | 요청사항 등 마지막 항목 전부 포함 |


## 예시 메일 내용
```java
고객명: 홍길동
전화번호: 010-1111-2222
이메일: test@naver.com
상품명: eSIM 10GB
수량: 2
요청사항: 오늘 중 발송해주세요
```
## Text Parser 연결 예시
HTML to Text 모듈의 결과를 Text Parser 모듈에 연결해 정규식을 적용한다.

![](https://velog.velcdn.com/images/duwnstj12/post/4828cc3a-8b16-40a2-9145-80319af588b2/image.png)
![](https://velog.velcdn.com/images/duwnstj12/post/274e2bb5-e7e7-4088-9675-797c13aef101/image.png)
![](https://velog.velcdn.com/images/duwnstj12/post/4df174d9-dc36-4da9-98dd-f06b2717cd8e/image.png)

## ✨다음 글 예고
다음 편에서는 아래 기능을 설명한다:

- ✅ Google Sheets에 고객 정보를 자동 저장하는 방법

- ✅ 외부 eSIM API로 POST 요청 보내는 방법

- ✅ 고객에게 이메일/카카오톡 알림 발송까지 구성





