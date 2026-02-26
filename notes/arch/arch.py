from diagrams import Diagram, Cluster
from diagrams.onprem.client import User
from diagrams.aws.security import Cognito
from diagrams.aws.compute import Lambda
from diagrams.aws.database import DynamodbTable

with Diagram(
    "AWS Auth - Cognito + Lambda + DynamoDB",
    filename="auth_architecture",
    show=False,
    direction="LR",
):
    spa = User("SPA Frontend")

    cognito_user_pool = Cognito("Cognito User Pool")
    cognito_client = Cognito("User Pool Client (SPA)")

    with Cluster("Auth Lambdas"):
        root_lambda = Lambda("root")
        signup_lambda = Lambda("signup")
        login_lambda = Lambda("login")
        factor2_question_lambda = Lambda("factor2_question")
        factor2_verify_lambda = Lambda("factor2_verify")
        factor3_challenge_lambda = Lambda("factor3_challenge")
        factor3_verify_lambda = Lambda("factor3_verify")

    with Cluster("Authentication State (DynamoDB)"):
        user_mfa_table = DynamodbTable("user_mfa\n(MFA settings)")
        tokens_table = DynamodbTable("tokens\n(short-lived tokens, TTL)")
        sessions_table = DynamodbTable("sessions\n(active sessions)")

    # Primary flows
    spa >> cognito_client >> cognito_user_pool

    # Requests from SPA to individual Lambdas
    spa >> root_lambda
    spa >> signup_lambda
    spa >> login_lambda
    spa >> factor2_question_lambda
    spa >> factor2_verify_lambda
    spa >> factor3_challenge_lambda
    spa >> factor3_verify_lambda

    # Lambdas interacting with Cognito and DynamoDB tables
    auth_lambdas = [
        root_lambda,
        signup_lambda,
        login_lambda,
        factor2_question_lambda,
        factor2_verify_lambda,
        factor3_challenge_lambda,
        factor3_verify_lambda,
    ]

    for fn in auth_lambdas:
        fn >> cognito_user_pool
        fn >> user_mfa_table
        fn >> tokens_table
        fn >> sessions_table