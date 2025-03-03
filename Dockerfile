FROM public.ecr.aws/lambda/python:3.8

# Set the working directory
WORKDIR /var/task

# Copy application files
COPY app.py requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install AWS Lambda Runtime Interface Client
RUN pip install awslambdaric

# Set the entrypoint and CMD for Lambda
ENTRYPOINT ["python", "-m", "awslambdaric"]
CMD ["app.lambda_handler"]