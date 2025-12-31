terraform {
  backend "s3" {
    bucket         = "tfstate-590183661886-eu-west-3"
    key            = "resources/nonlive/bball-app-template.tfstate"
    region         = "eu-west-3"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}