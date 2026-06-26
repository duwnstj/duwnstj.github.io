---
layout: post
title: "Failed to determine suitable jdbc url 에러"
date: 2024-08-19T00:57:06.623Z
tags:
  - 트러블 슈팅
---

# 오늘 겪은 트러블 슈팅
![](https://velog.velcdn.com/images/duwnstj12/post/8fc66b09-dc12-431d-bd9f-a3af5851b951/image.png)

- 이러한 에러가 나서 구글링을 해봤다.
- "Failed to determine suitable jdbc url" 오류는 JDBC (Java Database Connectivity) 연결 설정에서 문제가 발생했음을 나타낸다. 이 오류는 데이터베이스에 연결할 때 JDBC URL을 결정할 수 없다는 것을 의미한다.
- 따라서 Url 쪽을 확인을 해보았다.

## 에러가 나서 수정한 코드
![](https://velog.velcdn.com/images/duwnstj12/post/29d8f3ec-d5ce-4bb2-bb67-6dcbfb862f27/image.png)


- Application.properties 파일에서 url 부분이 잘못되었던 것이었다.
- spring이 만든 database 이름인데 spring이 아닌 테이블 이름인 plan으로 url을 정해놨었기 때문에 이러한 에러가 나는 것이었다.
- 따라서 plan을 spring으로 변경 후 에러가 해결 되었다.

## 에러 해결 후 결과

![](https://velog.velcdn.com/images/duwnstj12/post/3252f9a6-f142-40ff-b6a3-a2d5bd0ea601/image.png)

