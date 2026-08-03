
# Event Pipeline

Receives budget/anomaly alerts via SNS, reads the project's budget row from
DynamoDB, and logs a decision line.

Not done yet: real decision logic (approve/block/downgrade)

Files in this folder: `lambda_function.py`
