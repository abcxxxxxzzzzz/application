FROM alpine:3.21

RUN apk add --no-cache ca-certificates tzdata

ENV TZ=Asia/Shanghai

WORKDIR /app

COPY GinOne /app/GinOne

# 配置文件需要外部挂载
# docker run -v ./config:/app/config GinOne:latest

EXPOSE 18669

ENTRYPOINT ["/app/GinOne"]