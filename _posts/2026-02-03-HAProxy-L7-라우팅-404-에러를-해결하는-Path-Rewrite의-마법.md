---
layout: post
title: "[실습]HAProxy L7 라우팅: 404 에러를 해결하는 Path Rewrite의 마법"
date: 2026-02-03T09:58:32.702Z
categories:
  - Tech Log
---



### 1. 실습 개요 및 목표

Nginx보다 가용성이 높고 강력한 L7 기능을 제공하는 **HAProxy**를 실습해 보았습니다. 단순한 트래픽 분산을 넘어, 특정 URL 경로(Path)에 따라 서버를 할당하는 MSA 구조의 기초를 다지는 것이 목표입니다.

---

### 2. 시스템 흐름과 나의 이해

- **구조**: 클라이언트 → HAProxy → webserver 1, 2
- **특징**: `haproxy.cfg`를 통해 Frontend와 Backend를 세밀하게 설정할 수 있으며, 8404 포트의 **Stats UI**를 통해 트래픽 정보와 Health 체크 상태를 한눈에 볼 수 있습니다.
- **알고리즘**: 기본적으로 라운드 로빈(Round Robin)으로 균등하게 분산하지만, ACL 설정을 통해 특정 API URL(`path`)에 따라 원하는 서버로만 트래픽을 보낼 수 있습니다.

---

### 3. 정상 동작 확인 (Standard)

먼저 기본 로드 밸런싱 환경을 구축했습니다.



```bash
# 1. 네트워크 및 서버 생성
docker network create lab-net 2>/dev/null
docker run -d --name web1 --network lab-net nginx
docker run -d --name web2 --network lab-net nginx
```text
# 2. 서버 구분을 위한 index.html 수정

```bash
docker exec web1 sh -c "echo '<h1>THIS IS WEB - 1</h1>' > /usr/share/nginx/html/index.html"
docker exec web2 sh -c "echo '<h1>THIS IS WEB - 2</h1>' > /usr/share/nginx/html/index.html"`

```text
**[Troubleshooting]**
실습 중 8080 포트에서 자꾸 `web2`만 뜨는 현상이 있어 라운드 로빈이 안 되는 건가 의심했습니다. 하지만 **Stats UI**에서 `sessions` 토탈 수치를 확인한 결과, 실제로는 `web1`과 `web2` 모두 정상적으로 작동하고 있음을 확인했습니다. (로그를 실시간으로 보려면 `docker logs -f`를 활용하면 좋습니다.)

---

### 4. 시나리오: /item 접속 시 404 에러 발생

### 4.1 의도적 에러 상황과 가설

HAProxy에서 `/item` 주소 설정을 해주었는데 브라우저에서는 **404 에러**가 뜹니다.

- **원인**: HAProxy가 `/item`으로 트래픽을 전달하면, Nginx 서버는 `/usr/share/nginx/html/item` 폴더를 찾습니다. 하지만 서버 내부에는 해당 폴더가 없기 때문입니다.
- **고민**: "그럼 서버마다 `/item`, `/shop` 폴더를 다 만들어야 하나? 주소가 바뀌면 파일도 다 옮겨야 하나?"

### 4.2 해결: set-path (주소 세탁)

이 문제를 해결하는 것이 바로 **`http-request set-path /`** 설정입니다. 서버로 요청을 보내기 전 주소를 `/`로 치환해 주는 것이죠.

코드 스니펫

`backend item_servers
    # 요청 경로를 / 로 강제 치환 (Path Rewrite)
    # 이 설정 덕분에 서버에 /item 파일이 없어도 루트의 index.html을 보여줍니다.
    http-request set-path /
    server web1 web1:80 check`

---

### 5. 더 깊은 고민: "하위 폴더는 어떻게 가?"

하지만 `set-path /`를 쓰면 `/item/page1`으로 접속해도 무조건 루트(`/`)로 넘어가버리는 문제가 생깁니다. 이를 위해 **정규표현식**을 활용한 **`replace-path`**가 사실상 실무에서 무조건 필요한 이유입니다.

**[명령어 상세 설명]**

- **`http-request replace-path /item/(.*) /\1`**
    - **기능**: `/item/` 이라는 식별자만 떼어내고 뒷부분 경로는 보존합니다.
    - **세부사항**: `(.*)`가 기억한 파일명을 `\1`이 그대로 서버에 전달합니다.
    - **필수성**: 서버 내부의 물리적 구조를 노출하지 않으면서도 다양한 파일에 접근하기 위해 반드시 필요합니다.

---

### 6. 결론

강의의 `echo` 이미지와 달리 실제 `nginx` 이미지를 사용하면서 **"프록시는 주소를 번역해주고, 서버는 파일을 찾아준다"**는 매커니즘을 명확히 이해했습니다. 이제 운영팀에서 URL을 바꿔도 개발팀은 파일 수정 없이 HAProxy 설정 한 줄로 대응할 수 있습니다!