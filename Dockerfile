FROM public.ecr.aws/lambda/python:3.9

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

COPY chat_engine.py /var/lang/lib/python3.9/site-packages/canopy/chat_engine

# Copy function code
COPY main.py .env ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.ask_canopy_rag" ]
