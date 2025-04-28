USE QLSVNhom;
GO

-- c
--------------------------------------------------------------------------------
-- i) SP_INS_PUBLIC_NHANVIEN: sinh Asymmetric Key, hash MK, mã hóa LUONGCB, insert
--------------------------------------------------------------------------------
CREATE OR ALTER PROCEDURE SP_INS_PUBLIC_NHANVIEN
    @MANV    VARCHAR(20),
    @HOTEN   NVARCHAR(100),
    @EMAIL   VARCHAR(20),
    @LUONGCB INT,
    @TENDN   NVARCHAR(100),
    @MK      NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
	---------------------------------------------------
    -- 1) Kiểm tra lương khôg âm 
    ---------------------------------------------------
	IF @LUONGCB < 0
	BEGIN
		RAISERROR('Lương cơ bản không thể âm.', 16, 1);
		RETURN;
	END
    ---------------------------------------------------
    -- 1) Kiểm tra trùng
    ---------------------------------------------------
	IF EXISTS(SELECT 1 FROM NHANVIEN WHERE MANV = @MANV)
	BEGIN
		RAISERROR('MANV "%s" đã tồn tại, không thể insert.', 16, 1, @MANV);
		RETURN;
	END
    IF EXISTS(SELECT 1 FROM NHANVIEN WHERE TENDN = @TENDN)
    BEGIN
        RAISERROR('TENDN "%s" đã tồn tại, không thể insert.',16,1,@TENDN);
        RETURN;
    END

    ---------------------------------------------------
    -- 2) Drop key cũ (nếu có)
    ---------------------------------------------------
    DECLARE @sql NVARCHAR(MAX);
    IF EXISTS(SELECT 1 FROM sys.asymmetric_keys WHERE name = @MANV)
    BEGIN
        SET @sql = N'DROP ASYMMETRIC KEY ' + QUOTENAME(@MANV) + N';';
        EXEC sp_executesql @sql;
    END

    ---------------------------------------------------
    -- 3) Tạo Asymmetric Key mới (RSA_2048)
    ---------------------------------------------------
    BEGIN TRY
		SET @sql =  
			N'CREATE ASYMMETRIC KEY ' + QUOTENAME(@MANV) + N'
			  WITH ALGORITHM = RSA_2048
			  ENCRYPTION BY PASSWORD = N''' + REPLACE(@MK, N'''', N'''''') + N''';';
		EXEC sp_executesql @sql;
	END TRY
	BEGIN CATCH
		RAISERROR('Lỗi khi tạo khóa bất đối xứng: %s', 16, 1);
		RETURN;
	END CATCH

    ---------------------------------------------------
    -- 4) Hash mật khẩu MK với SHA1
    ---------------------------------------------------
    DECLARE @HASHED_MK VARBINARY(20);
    SET @HASHED_MK = HASHBYTES('SHA1', @MK);

    ---------------------------------------------------
    -- 5) Mã hóa lương với Asymmetric Key vừa tạo
    ---------------------------------------------------
    DECLARE @ENC_LUONG VARBINARY(MAX);
    SET @ENC_LUONG = 
        EncryptByAsymKey(
            AsymKey_ID(@MANV),
            CONVERT(VARBINARY(MAX), CONVERT(NVARCHAR(20), @LUONGCB))
        );

    ---------------------------------------------------
    -- 6) Insert vào NHANVIEN
    ---------------------------------------------------
    INSERT INTO NHANVIEN
        (MANV, HOTEN, EMAIL, LUONG, TENDN, MATKHAU, PUBKEY)
    VALUES
        (@MANV, @HOTEN, @EMAIL, @ENC_LUONG, @TENDN, @HASHED_MK, @MANV);
END
GO


--------------------------------------------------------------------------------
-- ii) SP_SEL_PUBLIC_NHANVIEN: mở key, giải mã LUONG, trả về MANV, HOTEN, EMAIL, LUONGCB
--------------------------------------------------------------------------------
CREATE OR ALTER PROCEDURE SP_SEL_PUBLIC_NHANVIEN
    @TENDN NVARCHAR(100),
    @MK    NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        -- Lấy MANV từ TENDN
        DECLARE @MANV VARCHAR(20);
        SELECT @MANV = MANV
        FROM NHANVIEN
        WHERE TENDN = @TENDN;

		-- Kiểm tra tồn tại khóa trước khi giải mã
		IF NOT EXISTS(SELECT 1 FROM sys.asymmetric_keys WHERE name = @MANV)
		BEGIN
			RAISERROR('Khóa bất đối xứng cho MANV "%s" không tồn tại.', 16, 1, @MANV);
			RETURN;
		END

        IF @MANV IS NULL
        BEGIN
            RAISERROR('Không tìm thấy nhân viên với TENDN = %s', 16, 1, @TENDN);
            RETURN;
        END

        -- Truy vấn và giải mã LUONG với password
        SELECT
            MANV,
            HOTEN,
            EMAIL,
            LUONGCB = TRY_CAST(
                CAST(
                    DecryptByAsymKey(AsymKey_ID(@MANV), LUONG, @MK) AS NVARCHAR(20)
                ) AS INT
            )
        FROM NHANVIEN
        WHERE TENDN = @TENDN;
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END
GO

--------------------------------------------------------------------------------
-- SP_LOGIN_NHANVIEN: Dang Nhap Voi Nhan Vien
--------------------------------------------------------------------------------
CREATE OR ALTER PROCEDURE SP_LOGIN_NHANVIEN
    @MANV NVARCHAR(100),
    @MATKHAU NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @HASHED_MK VARBINARY(20);
    SET @HASHED_MK = HASHBYTES('SHA1', @MATKHAU);

    IF EXISTS (
        SELECT 1
        FROM NHANVIEN
        WHERE MANV = @MANV AND MATKHAU = @HASHED_MK
    )
        SELECT 'LOGIN_SUCCESS' AS Status;
    ELSE
        SELECT 'LOGIN_FAIL' AS Status;
END
GO

--------------------------------------------------------------------------------
-- SP_GET_LOP_BY_NHANVIEN (Xem lớp mà nhân viên quản lý)
--------------------------------------------------------------------------------
CREATE OR ALTER PROCEDURE SP_GET_LOP_BY_NHANVIEN
    @MANV VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
	IF NOT EXISTS(SELECT 1 FROM NHANVIEN WHERE MANV = @MANV)
	BEGIN
		RAISERROR('Nhân viên với MANV "%s" không tồn tại.', 16, 1, @MANV);
		RETURN;
	END

    SELECT MALOP, TENLOP
    FROM LOP
    WHERE MANV = @MANV;
END
GO

--------------------------------------------------------------------------------
-- SP_GET_SINHVIEN_BY_LOP (Xem sinh viên thuộc lớp)
--------------------------------------------------------------------------------
CREATE OR ALTER PROCEDURE SP_GET_SINHVIEN_BY_LOP
    @MALOP VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
	IF NOT EXISTS(SELECT 1 FROM LOP WHERE MALOP = @MALOP)
	BEGIN
		RAISERROR('Lớp với MALOP "%s" không tồn tại.', 16, 1, @MALOP);
		RETURN;
	END

    SELECT MASV, HOTEN, NGAYSINH, DIACHI
    FROM SINHVIEN
    WHERE MALOP = @MALOP;
END
GO

--------------------------------------------------------------------------------
-- SP_INSERT_BANGDIEM (Nhập điểm thi, mã hóa điểm bằng PublicKey)
--------------------------------------------------------------------------------
CREATE OR ALTER PROCEDURE SP_INSERT_BANGDIEM
    @MASV VARCHAR(20),
    @MAHP VARCHAR(20),
    @DIEMTHI FLOAT,
    @PUBKEY VARCHAR(20) -- Chính là MANV, khóa công khai
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @ENCRYPTED_DIEM VARBINARY(MAX);

	IF NOT EXISTS(SELECT 1 FROM SINHVIEN WHERE MASV = @MASV)
	BEGIN
		RAISERROR('Sinh viên với MASV "%s" không tồn tại.', 16, 1, @MASV);
		RETURN;
	END
	IF NOT EXISTS(SELECT 1 FROM HOCPHAN WHERE MAHP = @MAHP)
	BEGIN
		RAISERROR('Học phần với MAHP "%s" không tồn tại.', 16, 1, @MAHP);
		RETURN;
	END
	IF @DIEMTHI < 0 OR @DIEMTHI > 10
	BEGIN
		RAISERROR('Điểm thi phải nằm trong khoảng từ 0 đến 10.', 16, 1);
		RETURN;
	END


    -- Mã hóa điểm
    BEGIN TRY
		SET @ENCRYPTED_DIEM = EncryptByAsymKey(
			AsymKey_ID(@PUBKEY),
			CONVERT(VARBINARY(MAX), CONVERT(NVARCHAR(20), @DIEMTHI))
		);
		INSERT INTO BANGDIEM (MASV, MAHP, DIEMTHI)
		VALUES (@MASV, @MAHP, @ENCRYPTED_DIEM);
	END TRY
	BEGIN CATCH
		RAISERROR('Lỗi khi mã hóa hoặc thêm điểm: %s', 16, 1);
		RETURN;
	END CATCH
END
GO
