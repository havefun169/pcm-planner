#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

aws_bucket="static-leya"

aws s3 sync --acl public-read "${ROOT_DIR}" "s3://${aws_bucket}/sims/PCM_PLANNER/v2/" --exclude "*.sh" --delete