"""Optional features of the .NET template, passed to the generators as a ``frozenset[str]``."""

# AWS S3 file storage: IFileStorageService (Application) backed by S3StorageService (Infrastructure).
S3 = "s3"

ALL = frozenset({S3})
