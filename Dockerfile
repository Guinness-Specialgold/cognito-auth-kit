# 1) Use the official AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# 2) Copy application code into the image
#    Keep the same layout you have now:
#    main.py
#    app/...
COPY main.py ./
COPY app ./app
COPY requirements.txt ./

# 3) Install dependencies *inside the Linux image*
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# 4) Tell Lambda which handler to call
#    This must match your function: def lambda_handler(event, context) in main.py
CMD ["main.lambda_handler"]
