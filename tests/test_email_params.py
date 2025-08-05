"""Tests for email parameter models."""

import time

import pytest
from pydantic import ValidationError

from microsoft_mcp.email_params import (
    BaseEmailParams,
    DeleteEmailParams,
    DraftEmailParams,
    EmptyTrashParams,
    FolderParams,
    ForwardEmailParams,
    ListEmailParams,
    MarkEmailParams,
    MoveEmailParams,
    ReplyEmailParams,
    SearchEmailParams,
    SendEmailParams,
)


class TestBaseEmailParams:
    """Test base parameter model."""
    
    def test_valid_base_params(self):
        """Test creating base params with valid values."""
        params = BaseEmailParams(account_id="user@example.com")
        assert params.account_id == "user@example.com"
    
    def test_missing_account_id(self):
        """Test that account_id is required."""
        with pytest.raises(ValidationError) as exc:
            BaseEmailParams()
        errors = exc.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("account_id",)
        assert errors[0]["type"] == "missing"
    
    def test_forbid_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc:
            BaseEmailParams(account_id="user@example.com", extra_field="not allowed")
        errors = exc.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("extra_field",)
        assert errors[0]["type"] == "extra_forbidden"


class TestListEmailParams:
    """Test list email parameter validation."""
    
    def test_valid_list_params(self):
        """Test creating list params with valid values."""
        params = ListEmailParams(
            account_id="user@example.com",
            folder="inbox",
            limit=50,
            include_body=True
        )
        assert params.folder == "inbox"
        assert params.limit == 50
        assert params.include_body is True
    
    def test_default_values(self):
        """Test default values for optional fields."""
        params = ListEmailParams(account_id="user@example.com")
        assert params.folder == "inbox"
        assert params.limit == 50
        assert params.skip == 0
        assert params.include_body is True
        assert params.has_attachments is None
        assert params.search_query is None
    
    def test_invalid_folder(self):
        """Test invalid folder value."""
        with pytest.raises(ValidationError) as exc:
            ListEmailParams(account_id="user@example.com", folder="invalid_folder")
        errors = exc.value.errors()
        assert errors[0]["type"] == "literal_error"
    
    def test_limit_boundaries(self):
        """Test limit field boundaries."""
        # Valid boundaries
        params = ListEmailParams(account_id="user@example.com", limit=1)
        assert params.limit == 1
        params = ListEmailParams(account_id="user@example.com", limit=250)
        assert params.limit == 250
        
        # Invalid boundaries
        with pytest.raises(ValidationError):
            ListEmailParams(account_id="user@example.com", limit=0)
        with pytest.raises(ValidationError):
            ListEmailParams(account_id="user@example.com", limit=251)


class TestSendEmailParams:
    """Test send email parameter validation."""
    
    def test_valid_send_params(self):
        """Test creating send params with valid values."""
        params = SendEmailParams(
            account_id="user@example.com",
            to="recipient@example.com",
            subject="Test Subject",
            body="Test body content"
        )
        assert params.to == ["recipient@example.com"]  # Normalized to list
        assert params.subject == "Test Subject"
        assert params.body == "Test body content"
    
    def test_multiple_recipients(self):
        """Test multiple recipients."""
        params = SendEmailParams(
            account_id="user@example.com",
            to=["user1@example.com", "user2@example.com"],
            subject="Test",
            body="Content",
            cc="cc@example.com",
            bcc=["bcc1@example.com", "bcc2@example.com"]
        )
        assert params.to == ["user1@example.com", "user2@example.com"]
        assert params.cc == ["cc@example.com"]
        assert params.bcc == ["bcc1@example.com", "bcc2@example.com"]
    
    def test_email_validation(self):
        """Test email address validation."""
        # Valid email formats
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user@subdomain.example.com"
        ]
        
        for email in valid_emails:
            params = SendEmailParams(
                account_id="user@example.com",
                to=email,
                subject="Test",
                body="Content"
            )
            assert params.to == [email.lower()]
        
        # Invalid email formats
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@@example.com",
            "user@example",
            ""
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError) as exc:
                SendEmailParams(
                    account_id="user@example.com",
                    to=email,
                    subject="Test",
                    body="Content"
                )
            # Check for either invalid format or empty email error
            error_str = str(exc.value)
            assert ("Invalid email format" in error_str or 
                    "Email address cannot be empty" in error_str)
    
    def test_email_normalization(self):
        """Test that email addresses are normalized to lowercase."""
        params = SendEmailParams(
            account_id="User@Example.COM",
            to="Recipient@EXAMPLE.COM",
            subject="Test",
            body="Content",
            cc=["CC@Example.Com"]
        )
        assert params.to == ["recipient@example.com"]
        assert params.cc == ["cc@example.com"]
    
    def test_subject_constraints(self):
        """Test subject field constraints."""
        # Empty subject should fail
        with pytest.raises(ValidationError):
            SendEmailParams(
                account_id="user@example.com",
                to="recipient@example.com",
                subject="",
                body="Content"
            )
        
        # Very long subject should fail
        with pytest.raises(ValidationError):
            SendEmailParams(
                account_id="user@example.com",
                to="recipient@example.com",
                subject="x" * 256,
                body="Content"
            )
    
    def test_attachments_normalization(self):
        """Test attachment path normalization."""
        params = SendEmailParams(
            account_id="user@example.com",
            to="recipient@example.com",
            subject="Test",
            body="Content",
            attachments="/path/to/file.pdf"
        )
        assert params.attachments == ["/path/to/file.pdf"]
        
        params = SendEmailParams(
            account_id="user@example.com",
            to="recipient@example.com",
            subject="Test",
            body="Content",
            attachments=["/file1.pdf", "/file2.docx"]
        )
        assert params.attachments == ["/file1.pdf", "/file2.docx"]


class TestDraftEmailParams:
    """Test draft email parameter validation."""
    
    def test_inherits_from_send_params(self):
        """Test that DraftEmailParams inherits from SendEmailParams."""
        params = DraftEmailParams(
            account_id="user@example.com",
            to="recipient@example.com",
            subject="Draft Subject",
            body="Draft content"
        )
        assert params.to == ["recipient@example.com"]
        assert params.draft_id is None
    
    def test_with_draft_id(self):
        """Test draft with existing draft ID."""
        params = DraftEmailParams(
            account_id="user@example.com",
            to="recipient@example.com",
            subject="Updated Draft",
            body="Updated content",
            draft_id="AAMkAGI2THQAA="
        )
        assert params.draft_id == "AAMkAGI2THQAA="


class TestReplyEmailParams:
    """Test reply email parameter validation."""
    
    def test_valid_reply_params(self):
        """Test creating reply params with valid values."""
        params = ReplyEmailParams(
            account_id="user@example.com",
            email_id="AAMkAGI2THQAA=",
            body="Thanks for your message."
        )
        assert params.email_id == "AAMkAGI2THQAA="
        assert params.body == "Thanks for your message."
        assert params.reply_all is False  # Default
        assert params.include_original is True  # Default
    
    def test_reply_all_flag(self):
        """Test reply_all flag."""
        params = ReplyEmailParams(
            account_id="user@example.com",
            email_id="AAMkAGI2THQAA=",
            body="Reply to all",
            reply_all=True
        )
        assert params.reply_all is True


class TestForwardEmailParams:
    """Test forward email parameter validation."""
    
    def test_valid_forward_params(self):
        """Test creating forward params with valid values."""
        params = ForwardEmailParams(
            account_id="user@example.com",
            email_id="AAMkAGI2THQAA=",
            to="colleague@example.com"
        )
        assert params.email_id == "AAMkAGI2THQAA="
        assert params.to == ["colleague@example.com"]
        assert params.comment is None
        assert params.include_attachments is True
    
    def test_with_comment(self):
        """Test forward with comment."""
        params = ForwardEmailParams(
            account_id="user@example.com",
            email_id="AAMkAGI2THQAA=",
            to=["user1@example.com", "user2@example.com"],
            comment="FYI - Please review"
        )
        assert params.comment == "FYI - Please review"
        assert len(params.to) == 2


class TestSearchEmailParams:
    """Test search email parameter validation."""
    
    def test_valid_search_params(self):
        """Test creating search params with valid values."""
        params = SearchEmailParams(
            account_id="user@example.com",
            query="project proposal"
        )
        assert params.query == "project proposal"
        assert params.folder is None
        assert params.limit == 50
    
    def test_date_filters(self):
        """Test date range filters."""
        params = SearchEmailParams(
            account_id="user@example.com",
            query="meeting",
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        assert params.start_date == "2024-01-01"
        assert params.end_date == "2024-12-31"
    
    def test_email_filters(self):
        """Test from/to email filters."""
        params = SearchEmailParams(
            account_id="user@example.com",
            query="invoice",
            from_address="vendor@example.com",
            to_address="accounting@company.com"
        )
        assert params.from_address == "vendor@example.com"
        assert params.to_address == "accounting@company.com"
    
    def test_invalid_email_filter(self):
        """Test invalid email in filters."""
        with pytest.raises(ValidationError) as exc:
            SearchEmailParams(
                account_id="user@example.com",
                query="test",
                from_address="invalid-email"
            )
        assert "Invalid email format" in str(exc.value)


class TestDeleteEmailParams:
    """Test delete email parameter validation."""
    
    def test_valid_delete_params(self):
        """Test creating delete params with valid values."""
        params = DeleteEmailParams(
            account_id="user@example.com",
            email_id="AAMkAGI2THQAA="
        )
        assert params.email_id == "AAMkAGI2THQAA="
        assert params.permanent is False  # Default
    
    def test_permanent_delete(self):
        """Test permanent delete flag."""
        params = DeleteEmailParams(
            account_id="user@example.com",
            email_id="AAMkAGI2THQAA=",
            permanent=True
        )
        assert params.permanent is True


class TestMoveEmailParams:
    """Test move email parameter validation."""
    
    def test_valid_move_params(self):
        """Test creating move params with valid values."""
        params = MoveEmailParams(
            account_id="user@example.com",
            email_id="AAMkAGI2THQAA=",
            destination_folder="archive"
        )
        assert params.email_id == "AAMkAGI2THQAA="
        assert params.destination_folder == "archive"
    
    def test_invalid_destination_folder(self):
        """Test invalid destination folder."""
        with pytest.raises(ValidationError):
            MoveEmailParams(
                account_id="user@example.com",
                email_id="AAMkAGI2THQAA=",
                destination_folder="invalid_folder"
            )


class TestMarkEmailParams:
    """Test mark email parameter validation."""
    
    def test_single_email_id(self):
        """Test marking single email."""
        params = MarkEmailParams(
            account_id="user@example.com",
            email_id="AAMkAGI2THQAA=",
            mark_as="read"
        )
        assert params.email_id == ["AAMkAGI2THQAA="]  # Normalized to list
        assert params.mark_as == "read"
    
    def test_multiple_email_ids(self):
        """Test marking multiple emails."""
        params = MarkEmailParams(
            account_id="user@example.com",
            email_id=["email1", "email2", "email3"],
            mark_as="unread"
        )
        assert len(params.email_id) == 3
        assert params.mark_as == "unread"
    
    def test_invalid_mark_as(self):
        """Test invalid mark_as value."""
        with pytest.raises(ValidationError):
            MarkEmailParams(
                account_id="user@example.com",
                email_id="AAMkAGI2THQAA=",
                mark_as="invalid_status"
            )


class TestFolderParams:
    """Test folder operation parameter validation."""
    
    def test_list_operation(self):
        """Test list folders operation."""
        params = FolderParams(
            account_id="user@example.com",
            operation="list"
        )
        assert params.operation == "list"
        assert params.folder_name is None
    
    def test_create_operation(self):
        """Test create folder operation."""
        params = FolderParams(
            account_id="user@example.com",
            operation="create",
            folder_name="Project Alpha"
        )
        assert params.operation == "create"
        assert params.folder_name == "Project Alpha"
    
    def test_rename_operation(self):
        """Test rename folder operation."""
        params = FolderParams(
            account_id="user@example.com",
            operation="rename",
            folder_name="Old Name",
            new_name="New Name"
        )
        assert params.operation == "rename"
        assert params.folder_name == "Old Name"
        assert params.new_name == "New Name"
    
    def test_missing_required_fields(self):
        """Test missing required fields for operations."""
        # Create without folder_name
        with pytest.raises(ValidationError) as exc:
            FolderParams(
                account_id="user@example.com",
                operation="create"
            )
        assert "folder_name is required for create operation" in str(exc.value)
        
        # Rename without new_name
        with pytest.raises(ValidationError) as exc:
            FolderParams(
                account_id="user@example.com",
                operation="rename",
                folder_name="Old Name"
            )
        assert "new_name is required for rename operation" in str(exc.value)


class TestEmptyTrashParams:
    """Test empty trash parameter validation."""
    
    def test_valid_empty_trash_params(self):
        """Test creating empty trash params with valid values."""
        params = EmptyTrashParams(
            account_id="user@example.com",
            confirm=True
        )
        assert params.confirm is True
    
    def test_confirm_required(self):
        """Test that confirm field is required."""
        with pytest.raises(ValidationError):
            EmptyTrashParams(account_id="user@example.com")


class TestPerformanceBenchmarks:
    """Test validation performance benchmarks."""
    
    def test_simple_validation_performance(self):
        """Test that simple validations complete in <5ms."""
        start = time.time()
        for _ in range(100):
            params = BaseEmailParams(account_id="user@example.com")
        elapsed = (time.time() - start) / 100 * 1000  # ms per validation
        
        assert elapsed < 5, f"Simple validation took {elapsed:.2f}ms (target: <5ms)"
    
    def test_complex_validation_performance(self):
        """Test that complex validations complete in <5ms."""
        start = time.time()
        for _ in range(100):
            params = SendEmailParams(
                account_id="user@example.com",
                to=["user1@example.com", "user2@example.com"],
                subject="Test Subject",
                body="Test body content",
                cc=["cc1@example.com", "cc2@example.com"],
                bcc="bcc@example.com",
                attachments=["/file1.pdf", "/file2.docx"],
                importance="high"
            )
        elapsed = (time.time() - start) / 100 * 1000  # ms per validation
        
        assert elapsed < 5, f"Complex validation took {elapsed:.2f}ms (target: <5ms)"
    
    def test_validation_error_performance(self):
        """Test that validation errors are generated quickly."""
        start = time.time()
        for _ in range(100):
            try:
                params = SendEmailParams(
                    account_id="user@example.com",
                    to="invalid-email",
                    subject="Test",
                    body="Content"
                )
            except ValidationError:
                pass
        elapsed = (time.time() - start) / 100 * 1000  # ms per validation
        
        assert elapsed < 5, f"Error validation took {elapsed:.2f}ms (target: <5ms)"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_strings(self):
        """Test handling of empty strings."""
        # Empty email should fail
        with pytest.raises(ValidationError):
            SendEmailParams(
                account_id="",
                to="recipient@example.com",
                subject="Test",
                body="Content"
            )
        
        # Empty body should be allowed
        params = SendEmailParams(
            account_id="user@example.com",
            to="recipient@example.com",
            subject="Test",
            body=""
        )
        assert params.body == ""
    
    def test_null_optional_fields(self):
        """Test that optional fields can be None."""
        params = SendEmailParams(
            account_id="user@example.com",
            to="recipient@example.com",
            subject="Test",
            body="Content",
            cc=None,
            bcc=None,
            attachments=None
        )
        assert params.cc is None
        assert params.bcc is None
        assert params.attachments is None
    
    def test_special_characters_in_subject(self):
        """Test special characters in subject."""
        special_subjects = [
            "Test with émoji 🚀",
            "Test with 中文字符",
            "Test with symbols !@#$%^&*()",
            "Test with\nnewline",
            "Test with\ttab"
        ]
        
        for subject in special_subjects:
            params = SendEmailParams(
                account_id="user@example.com",
                to="recipient@example.com",
                subject=subject,
                body="Content"
            )
            assert params.subject == subject
    
    def test_very_long_email_lists(self):
        """Test handling of very long recipient lists."""
        recipients = [f"user{i}@example.com" for i in range(100)]
        params = SendEmailParams(
            account_id="user@example.com",
            to=recipients,
            subject="Mass email",
            body="Content"
        )
        assert len(params.to) == 100
        assert all(email.startswith("user") for email in params.to)