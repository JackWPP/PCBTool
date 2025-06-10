from fastapi import HTTPException, status


class PCBToolException(Exception):
    """基础异常类"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(PCBToolException):
    """认证错误"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(PCBToolException):
    """授权错误"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundError(PCBToolException):
    """资源未找到错误"""
    def __init__(self, message: str = "资源未找到"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationError(PCBToolException):
    """验证错误"""
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class FileUploadError(PCBToolException):
    """文件上传错误"""
    def __init__(self, message: str = "文件上传失败"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class ExternalAPIError(PCBToolException):
    """外部API调用错误"""
    def __init__(self, message: str = "外部API调用失败"):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY)


class TaskError(PCBToolException):
    """任务处理错误"""
    def __init__(self, message: str = "任务处理失败"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_http_exception(exc: PCBToolException) -> HTTPException:
    """将自定义异常转换为HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )
