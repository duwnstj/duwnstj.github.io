---
layout: post
title: "Spring Security로 전환하면서 발생한 AuthUser 문제 트러블슈팅
"
date: 2024-10-11T01:44:51.623Z
tags:
  - 트러블 슈팅
---

## 문제 상황
- 개인과제를 진행하면서 일정을 저장 중 문제가 발생했습니다. 
- 기존에는 JWT를 사용해 로그인한 유저의 정보를 가져올 때 아무 문제가 없었지만, Spring security로 변환한 후 일정을 저장할 때 `AuthUser`의 정보가 `null`값으로 처리되는 문제가 발생했습니다.

## 문제가 생겼던 코드
![](https://velog.velcdn.com/images/duwnstj12/post/99d0ea44-f9c5-4c50-a4b2-bf641c635127/image.png)

기존 JWT를 사용할 때는 `AuthUser`에 값을 전달하기 위해 `@Auth`라는 커스텀 어노테이션을 만들어 사용했습니다. 이는 JWT가 해당 정보를 인식하도록 하기 위해 필요했습니다.

## 커스텀한 @Auth 어노테이션 코드
```java
package org.example.expert.domain.common.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
public @interface Auth {
}

```
## AuthUser 코드
```java
package org.example.expert.domain.common.dto;

import lombok.Getter;
import org.example.expert.domain.user.enums.UserRole;

@Getter
public class AuthUser {

    private final Long id;
    private final String email;
    private final UserRole userRole;

    public AuthUser(Long id, String email, UserRole userRole) {
        this.id = id;
        this.email = email;
        this.userRole = userRole;
    }
}

```
필터에서 먼저 request(요청)으로 들어온 값에서 필요한 정보들을 추출 한뒤 `AuthUserArgumentResolver`를 사용해 AuthUser라는 클래스로 값을 받아서 사용했습니다.

## 문제의 원인
문제는 Spring Security로 변환할 때도 그대로 사용했기 때문에 발생했습니다. `Spring security`에서는 `@AuthenticationPrincipal` 어노테이션을 사용하여 로그인된 유저의 정보를 가져올 수 있습니다. 그 이유는 `Authentication.AbstractAuthenticationToken` 객체의 `getPrincipal()` 메서드를 통해 사용자 정보를 얻기 때문입니다.

## Principal 관련 코드 
```java
 @Override
    public Object getPrincipal() {
        return authUser;
    }
```
이 코드는 이전에 `AuthUserArgumentResolver`를 통해 `AuthUser`에 값을 넘겨준 코드와 동일한 방식입니다. 따라서 Spring Security에서는 `@AuthenticationPrincipal` 어노테이션을 사용하면 로그인된 유저 정보를 편리하게 가져올 수 있습니다.

## 문제 해결 코드
```java
@PostMapping("/todos")
    public ResponseEntity<TodoSaveResponse> saveTodo(
            @AuthenticationPrincipal AuthUser authUser,
            @Valid @RequestBody TodoSaveRequest todoSaveRequest
    ) {
        return ResponseEntity.ok(todoService.saveTodo(authUser, todoSaveRequest));
    }

```
이렇게 매개변수에 `@AuthenticationPrincipal` 어노테이션을 사용하여 로그인된 유저 정보를 전달받을 수 있었고 문제없이 일정을 저장할 수 있었습니다.

## 결과

![](https://velog.velcdn.com/images/duwnstj12/post/acb1bcf4-e414-4895-a5a6-88d5290aabc3/image.png)


