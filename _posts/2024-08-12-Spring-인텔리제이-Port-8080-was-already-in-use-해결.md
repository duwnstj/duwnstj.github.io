---
layout: post
title: "[Spring] 인텔리제이 Port 8080 was already in use 해결"
date: 2024-08-12T08:05:22.043Z
categories:
  - Backend
tags:
  - 트러블 슈팅
---

## 스프링 공부 중 생긴 트러블 슈팅
- 오늘 인텔리제이로 gradle을 세팅하고 스프링 부트 프로젝트를 만들었는데 이 프로젝트를 실행하였더니 아래 이미지와 같은 에러가 뜨게 되었다.

![](https://velog.velcdn.com/images/duwnstj12/post/640f7c9e-c12c-4c53-a664-e240df48c995/image.png)

- 구글링을 통해 에러 메시지를 찾아보니 8080 포트 번호를 사용하고 있어서 뜨는 에러라고 한다. 이전에 STS를 통해서 사용했던 8080포트 번호가 있어서 인텔리제이에서 떴던것같다.

## 해결 방법
- Window 기준 cmd(명령프롬프트)를 관리자 권한으로 실행으로 실행 시킨다.
![](https://velog.velcdn.com/images/duwnstj12/post/08bae65d-7dc1-4612-a7b0-d80d7de9bcdc/image.png)
- netstat -a -o 8080(포트번호)에 해당하는 PID 번호를 찾아준다.
![](https://velog.velcdn.com/images/duwnstj12/post/fea89d6a-82b8-444b-9b55-2927545c9df3/image.png)
- 윈도우 기준 ctrl+c를 눌러 명령어를 빠져나와서 다시 `taskkill /pid 6236(PID번호) /f` 이 명령어를 눌러준다.
- 이 명령어를 입력하면 8080 포트 번호를 종료시켜준다. 
- cmd 창을 종료 시킨 후 다시 인텔리제이에서 실행 시켜 주면 인텔리제이가 잘 실행되는 것을 확인 할 수 있다.

## 결과

![](https://velog.velcdn.com/images/duwnstj12/post/a7e94d4e-7de9-4d6e-9e3d-d04d0011fe4d/image.png)
