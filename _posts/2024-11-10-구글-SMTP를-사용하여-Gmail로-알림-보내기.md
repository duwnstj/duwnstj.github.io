---
layout: post
title: "구글 SMTP를 사용하여 Gmail로 알림 보내기"
date: 2024-11-10T07:49:40.945Z
categories:
  - Tech Log
tags:
  - 최종프로젝트
---

## 개요 
- 최종 프로젝트에서 **도서관 알림 기능**을 구현하게 되었습니다.
알림 기능은 책 대여 기한이 임박하거나 스터디룸 예약 일정이 다가올 때 사용자에게 미리 알려주는 역할을 합니다. 이를 구현하기 위해 **스케줄러**를 활용하여 특정 시점에 알림을 보낼 수 있도록 설정했습니다.

알림 전달 방식으로는 이메일을 선택했고, **구글 SMTP**를 이용해 Gmail로 알림을 보낼 수 있도록 구현했습니다.
이 글에서는 구글 SMTP를 사용하여 Gmail로 알림을 보내는 과정을 단계별로 설명하겠습니다.

## 구글 SMTP란?
- **구글 SMTP**는 Gmail 계정을 사용하여 이메일을 전송할 수 있는 프로토콜 서비스입니다. 이를 통해 애플리케이션이나 프로그램에서 시스템 알림, 인증 메일 등을 쉽게 전송할 수 있습니다.

### 구글 SMTP의 주요 특징
**1. 간단한 설정** : 별도의 메일 서버 없이 Gmail 계정을 활용
**2. 보안 지원** : SSL/TLS 암호화를 통한 안전한 메일 전송
**3. 테스트 용이성** : 개발 환경에서 쉽게 이메일 전송 기능 확인

## 구글 SMTP 사용 방법
구글 SMTP를 사용하려면 먼저 IMAP를 활성화하고, 앱 비밀번호를 생성해야 합니다.

### 1. IMAP 활성화하기 
IMAP는 Gmail 계정에 접근할 수 있도록 설정하는 기능입니다. 이를 활성화하지 않으면 애플리케이션에서 Gmail을 사용할 수 없습니다.
1. **Gmail 설정**에 들어가 **전달 및 POP/IMAP** 탭으로 이동합니다.
2. **IMAP 사용**을 체크한 뒤 **변경 사항 저장**을 클릭합니다.
![](https://velog.velcdn.com/images/duwnstj12/post/65375a18-7d14-4f85-abd5-ce64fe9f1359/image.png)


### 앱 비밀번호 생성
구글 SMTP를 사용하려면 앱 비밀번호가 필요합니다.
구글 계정으로 들어가 보안 탭을 들어갑니다.
![](https://velog.velcdn.com/images/duwnstj12/post/42ab7b4a-690a-46a3-ab9f-da180cb89e6b/image.png)

검색창에 `앱 비밀번호`를 검색해줍니다.
![](https://velog.velcdn.com/images/duwnstj12/post/28d19498-0f82-4d08-bb71-aedec5725fe2/image.png)

앱 비밀번호를 아래와 같이 생성해줍니다.
![](https://velog.velcdn.com/images/duwnstj12/post/66643094-837a-4254-89fe-b7f139a662cb/image.png)

**참고** : 처음에 생성할 때만 앱 비밀번호를 확인할 수 있습니다.

## SMTP 서버 정보
구글 SMTP 서버를 설정할 때 필요한 정보는 다음과 같습니다.
![](https://velog.velcdn.com/images/duwnstj12/post/38141b66-e423-4693-8c8e-fcf6e27b247a/image.png)

## Java로 구글 SMTP 사용하기 

### 1. `JavaMail` 라이브러리 추가
`build.gradle`파일에 `JavaMail`라이브러리를 추가합니다.

{% highlight java %}
 // mail 송신을 위한 의존성
    implementation 'org.springframework.boot:spring-boot-starter-mail'
{% endhighlight %}
## 2.SMTP 설정 application.yml
SMTP에 필요한 정보를 application.yml 파일에 저장합니다.

{% highlight java %}
spring:  
  mail:  
    host: smtp.gmail.com  
    port: 587  
    username: ${USER_NAME}  
    password: ${USER_PASSWORD}  
    properties.mail.smtp:  
      auth: true  
      starttls.enable: true  

{% endhighlight %}
하지만 우리 프로젝트에서는 `JavaMailSender`가 자동으로 빈 등록이 되지 않는 문제가 있었습니다. 따라서 수동으로 빈 등록을 해주었습니다.

## 수동으로 빈 등록
{% highlight java %}
@Configuration
public class MailConfig {

    @Bean
    public JavaMailSender mailSender(){
        JavaMailSenderImpl mailSender = new JavaMailSenderImpl();
        mailSender.setHost("smtp.gmail.com");
        mailSender.setPort(587);
        mailSender.setUsername(System.getenv("USER_NAME"));
        mailSender.setPassword(System.getenv("USER_PASSWORD"));

        Properties props = mailSender.getJavaMailProperties();
        props.put("mail.transport.protocol", "smtp");
        props.put("mail.smtp.auth", "true");
        props.put("mail.smtp.starttls.enable", "true");
        props.put("mail.debug", "true");

        return mailSender;
    }
}
{% endhighlight %}
***

## 스케줄러를 사용한 알림 전송
스케줄러를 통해 특정 시간에 알림을 자동으로 전송할 수 있습니다.

### 스케줄러 코드
{% highlight java %}
 //매일 오전 8시 30에  대여 및 스터디룸 예약 알림을 자동으로 전송
    @Scheduled(cron = "0 30 8 * * ?")
    public void sendReminders() {


        RLock lock = redissonClient.getLock("NotificationSchedulerLock");
        try {
            //watchDog로 락 갱신 연장
            lock.lock(10, TimeUnit.MINUTES);
            //대여 알림 전송
            rentalNotifyService.sendRentalReminders();
            //스터디룸 예약 알림 전송
            studyRoomNotifyService.sendReservationReminders();
        } catch (Exception e) {
            log.error("알림 전송 중 에러가 발생했습니다. ", e);
        } finally {
            if (lock.isHeldByCurrentThread()) {// 현재 스레드가 락을 보유하고 있는 지 확인
                lock.unlock(); // 락을 보유하고 있다면 락 해제
            }

        }
    }
{% endhighlight %}
이 코드는 매일 오전 8시 30에 알림을 전송하며 **Redisson 분산 락**을 사용해 동시성 제어 문제를 방지했습니다.

## 도서관 책 반납일 임박 알림 서비스 코드
{% highlight java %}
  private final BookRentalRepository bookRentalRepository;
    private final NotificationService notificationService;

    //반납 기한에 따른 알림을 생성하는 메서드
    public void sendRentalReminders() {

        List<BookRental> rentalsDueIn3Days = getRentalsDueInRange(3);
        sendReminderForDueDate(rentalsDueIn3Days,3,"책 반납일 3일전입니다 책 반납 준비해주세요");
        sendReminderForDueDate(rentalsDueIn3Days,1,"책 반납일 1일전입니다. 책 반납 준비해주세요");
        sendReminderForDueDate(rentalsDueIn3Days,0,"책 반납일입니다. 책 반납해주세요");
    }

    // 대여 반납일을 기준으로 알림 보내기
    public void sendReminderForDueDate(List<BookRental> rentals, int daysBefore, String message) {

        List<BookRental> filterRentals = rentals.stream()
                .filter(bookRental -> bookRental.getRentalDate().plusDays(7)
                        .toLocalDate().isEqual(LocalDate.now().plusDays(daysBefore))
                ).toList();
        sendReminders(filterRentals, message);

    }


    // 알람 생성 로직으로 알람을 보낼 사람들의 정보를 보내는 메서드
    public void sendReminders(List<BookRental> rentalList, String message) {


        for (BookRental list : rentalList) {
            User user = list.getUser();
            NotificationRequestDto requestDto = new NotificationRequestDto(user.getId(), message);
            notificationService.createNotification(requestDto);

        }
    }

    // 반납 기한이 n일 후인 대여 정보를 조회하는 메서드
    public List<BookRental> getRentalsDueInRange(int days) {
        LocalDateTime startDate = LocalDate.now().minusDays(7).atStartOfDay();
        LocalDateTime endDate = LocalDate.now().plusDays(days).atTime(LocalTime.MAX); // 현재 날짜 + dayBefore
        return bookRentalRepository.findAllRentalDateBetween(startDate, endDate);

    }

{% endhighlight %}
필터링을 하여 해당하는 유저에게 보낼 알림을 데이터베이스에 저장을 하고 그 후 Gmail로 알림을 보내는 로직입니다.

## NotificationService 코드

### 이메일 전송
{% highlight java %}
package com.example.library_management.domain.common.notification.service;

import com.example.library_management.domain.common.notification.dto.NotificationRequestDto;
import com.example.library_management.domain.common.notification.entity.Notification;
import com.example.library_management.domain.common.notification.repository.NotificationRepository;
import com.example.library_management.domain.user.entity.User;
import com.example.library_management.domain.user.exception.NotFoundUserException;
import com.example.library_management.domain.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class NotificationService {
    private final NotificationRepository notificationRepository;
    private final UserRepository userRepository;
    private final JavaMailSender mailSender;

    //새로운 알림 생성 후 저장

    public void createNotification(NotificationRequestDto requestDto) {
        User user = userRepository.findById(requestDto.getUserId())
                .orElseThrow(NotFoundUserException::new);

        Notification notification = new Notification(user, requestDto.getMessage());


        notificationRepository.save(notification);

        sendEmailNotifications();
    }

    //이메일로 전송되지 않은 알림 전송
    public void sendEmailNotifications() {


        List<Notification> unNotificationList = notificationRepository.findBySentFalse();

        for (Notification notification : unNotificationList) {
            User user = notification.getUser();
            String email = user.getEmail();
            String message = notification.getMessage();

            sendEmail(email, message);

            // 보낸 메시지는 true로 변경하여 중복 메시지 송신을 방지
            notification.updateAsSent();
        }
    }

    //실제 이메일 전송 로직
    public void sendEmail(String toEmail, String message) {

        SimpleMailMessage mailMessage = new SimpleMailMessage();
        mailMessage.setTo(toEmail);
        mailMessage.setSubject("도서관 알림");
        mailMessage.setText(message);

        mailSender.send(mailMessage);

        log.info("이메일을 성공적으로 보냈습니다.");
    }


}

{% endhighlight %}
## 결론
구글 SMTP를 활용하면 **안전하고 간단하게 이메일 알림 기능**을 구현할 수 있습니다.
이글에서는 Gmail을 통해 사용자에게 도서관 대여 및 예약 알림을 전송하는 과정을 소개했습니다.







