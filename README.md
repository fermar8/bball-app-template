# bball-app-template
A template repository for building Go applications with AWS Lambda.

## Overview
This repository provides a basic AWS Lambda function template written in Go. The Lambda handler receives events and processes them, currently logging a message to CloudWatch.

## Prerequisites
- Go 1.24 or later
- AWS Lambda environment for deployment

## Project Structure
```
.
├── main.go          # Lambda handler implementation
├── main_test.go     # Unit tests for the handler
├── go.mod           # Go module definition
└── go.sum           # Go module dependencies
```

## Building
To build the application:
```bash
go build
```

## Testing
To run the unit tests:
```bash
go test -v
```

## Handler Function
The `HandleRequest` function processes Lambda events and logs "Processing template handler" to CloudWatch. It accepts any event type and returns a success message.

## Usage
This is a template repository. You can use it as a starting point for building your own Go-based AWS Lambda functions.

1. Clone or use this template to create a new repository
2. Modify the `HandleRequest` function in `main.go` to implement your business logic
3. Add corresponding tests in `main_test.go`
4. Build and deploy to AWS Lambda
