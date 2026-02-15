# AWS SNS (Simple Notification Service)

SNS is a managed publish–subscribe messaging service. Publishers send messages to topics; subscribers receive them via HTTP(S), email, SMS, or mobile push. It supports one-to-many delivery and is used for event distribution and alerting.
# AWS SQS (Simple Queue Service)

SQS is a managed message queue. Producers send messages to queues, consumers retrieve and process them asynchronously. Standard queues offer high throughput, FIFO queues provide exactly-once delivery and ordering. SQS is used for decoupling components and buffering workloads.
Integration

SNS can deliver messages to multiple SQS queues, combining fan-out delivery with SQS’s durability and retry handling.


AWS docs Fan-out pattern SNS to SQS
https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html


AWS guide on when to use SNS, SQS 
https://docs.aws.amazon.com/decision-guides/latest/sns-or-sqs-or-eventbridge/sns-or-sqs-or-eventbridge.html


## Summary: SNS and SQS in this application

We can publish an event once to SNS (e.g. “user requested a service”). SNS then sends that same event to every subscriber you’ve configured.

Those subscribers can be different types:

- Email – SNS sends directly to the user’s email.
- SQS queues – SNS sends the event into one or more queues. Each queue can have its own Lambda that processes the event.

So one event can trigger both:

1. Immediate notifications – SNS sends straight to email, so the user gets a confirmation quickly.

2. Background work – SNS sends the same event into an SQS queue, and a Lambda runs later to do things like approvals, analytics, or updates.

You don’t need to call email and the queue separately. You publish once to SNS, and it fans out to all subscribers. That keeps the code simple and lets you add new subscribers (e.g. another queue or SMS) without changing the publisher.