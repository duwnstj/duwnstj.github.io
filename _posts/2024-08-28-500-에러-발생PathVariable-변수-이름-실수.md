---
layout: post
title: "500 에러 발생:PathVariable 변수 이름 실수"
date: 2024-08-28T13:36:26.207Z
categories:
  - Tech Log
tags:
  - 트러블 슈팅
---

## 오늘 겪은 트러블 슈팅
![](https://velog.velcdn.com/images/duwnstj12/post/e14a6a88-b4d0-4f17-a51b-26b0f5bf82d9/image.png)

오늘 개발 중 API 호출을 할 때 500 Internal Server Error를 겪게 되었다. 

## 1. 문제 상황
Postman으로 댓글 생성 API에 요청을 보냈을 때 예상치 못한 500 에러가 발생했다. 해당 API는 특정 일정(`schedule`)에 댓글을 생성하는 기능을 담당하는데 아래는 문제를 일으킨 기존 코드이다.

### 기존 코드
```java
@PostMapping("/{id}")
public ResponseEntity<CommentResponseDto> createComment(@PathVariable Long scheduleId, @RequestBody CommentRequestDto commentRequestDto) {
    CommentResponseDto saveComment = commentService.createComment(scheduleId, commentRequestDto);

    return ResponseEntity.ok(saveComment);
}
```
이 코드를 분석해보니 문제의 원인을 찾을 수 있었다.

## 2. 문제 원인 
- 변수 이름 불일치 : URL 경로에서 `id`라는 이름을 사용하고 있지만, 메서드의 파라미터 이름은 `scheduleId`를 사용하고 있었다. `@PathVariable` 애노테이션은 URL 경로의 `{}`안에 지정된 변수 이름과 메소드 파라미터의 이름이 일치해야 값을 제대로 전달 할 수 있다.

이 불일치로 인해 `scheduleId` 값이 제대로 전달되지 않아서, 서비스 계층에서 오류가 발생한것이다.

## 3. 해결 방법
이 문제를 해결하기 위해 코드를 아래와 같이 수정했다.

### 수정한 코드

```java
@PostMapping("/{scheduleId}")
public ResponseEntity<CommentResponseDto> createComment(@PathVariable Long scheduleId, @RequestBody CommentRequestDto commentRequestDto) {
    CommentResponseDto saveComment = commentService.createComment(scheduleId, commentRequestDto);

    return ResponseEntity.ok(saveComment);
}

```
수정한 내용은 이러하다.
- URL 경로의 `{id}`를 `{scheduleId}`로 수정하여 메서드 파라미터 이름과 일치시켰다. 

## 4. 결과
코드를 수정한 후 , Postman을 통해 다시 요청을 보내본 결과, API가 정상적으로 작동했다. 이 경험을 통해 변수 이름 일치의 중요성을 다시 한번 확인하였다.
- 아래는 API가 정상적으로 작동한 사진이다.

![](https://velog.velcdn.com/images/duwnstj12/post/a49486ca-3473-43c2-a9aa-f3c11656bb16/image.png)
