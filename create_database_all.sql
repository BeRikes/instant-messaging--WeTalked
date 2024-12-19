USE InstantMessagingDB;
GO

-- �����û���
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY, -- �Զ�����������
    Username NVARCHAR(50) NOT NULL UNIQUE, -- �û������������ظ�
    PasswordHash VARBINARY(64) NOT NULL, -- ��ϣ�������
    Email NVARCHAR(100) NOT NULL UNIQUE, -- �����ʼ���ַ���������ظ�
    PhoneNumber NVARCHAR(20), -- ��ѡ�ĵ绰����
    CreatedAt DATETIME DEFAULT GETDATE(), -- ����ʱ�䣬Ĭ�ϵ�ǰʱ��
    LastLogin DATETIME, -- ����¼ʱ��
    IsActive BIT DEFAULT 1 -- �˻��Ƿ񼤻Ĭ�ϼ���
);

-- �������ѹ�ϵ��
CREATE TABLE Friendships (
    FriendshipID INT IDENTITY(1,1) PRIMARY KEY, -- �Զ�����������
    User1ID INT NOT NULL, -- ��һ���û�ID
    User2ID INT NOT NULL, -- �ڶ����û�ID
    Status_ NVARCHAR(20) NOT NULL CHECK (Status_ IN ('Pending', 'Accepted', 'Rejected')), -- ��ϵ״̬
    CreatedAt DATETIME DEFAULT GETDATE(), -- ����ʱ�䣬Ĭ�ϵ�ǰʱ��
    CONSTRAINT FK_Friendship_User1 FOREIGN KEY (User1ID) REFERENCES Users(UserID),
    CONSTRAINT FK_Friendship_User2 FOREIGN KEY (User2ID) REFERENCES Users(UserID),
    CONSTRAINT CHK_Friendship_DistinctUsers CHECK (User1ID <> User2ID), -- ȷ�������û�����ͬһ��
    CONSTRAINT UQ_Friendship_UniquePair UNIQUE (User1ID, User2ID) -- ȷ��һ���û�֮��Ĺ�ϵΨһ
);

-- ������Ϣ��
CREATE TABLE Messages_ (
    MessageID BIGINT IDENTITY(1,1) PRIMARY KEY, -- �Զ������Ĵ���������
    SenderID INT NOT NULL, -- ������ID
    ReceiverID INT NOT NULL, -- ������ID
    Content NVARCHAR(MAX) NOT NULL, -- ��Ϣ����
    SentAt DATETIME DEFAULT GETDATE(), -- ����ʱ�䣬Ĭ�ϵ�ǰʱ��
    IsRead BIT DEFAULT 0, -- �Ƿ��Ѷ���Ĭ��δ��
    CONSTRAINT FK_Message_Sender FOREIGN KEY (SenderID) REFERENCES Users(UserID),
    CONSTRAINT FK_Message_Receiver FOREIGN KEY (ReceiverID) REFERENCES Users(UserID)
);

-- ����������Ż���ѯ����
-- �����û���ͨ�����ǻ�Ծ�����ѯ���ֶν�������
CREATE INDEX IX_Users_Username ON Users(Username);
CREATE INDEX IX_Users_Email ON Users(Email);

-- ���ں��ѹ�ϵ��ȷ�����ٲ����ض��û�����ϵ���б�
CREATE INDEX IX_Friendships_User1ID ON Friendships(User1ID);
CREATE INDEX IX_Friendships_User2ID ON Friendships(User2ID);

-- ������Ϣ���Ż����ݷ����ߡ��������Լ�����ʱ��Ĳ�ѯ
CREATE INDEX IX_Messages_SenderID ON Messages_(SenderID);
CREATE INDEX IX_Messages_ReceiverID ON Messages_(ReceiverID);
CREATE INDEX IX_Messages_SentAt ON Messages_(SentAt);
CREATE INDEX IX_Messages_IsRead ON Messages_(IsRead);

-- �����ҪƵ���ذ��շ����ߺͽ����ߵ���Ͻ��в�ѯ�����Դ�����������
CREATE INDEX IX_Messages_SenderID_ReceiverID ON Messages_(SenderID, ReceiverID);

-- ����Ⱥ���
CREATE TABLE Groups (
    GroupID INT IDENTITY(1,1) PRIMARY KEY, -- �Զ�����������
    GroupName NVARCHAR(100) NOT NULL, -- Ⱥ������
    OwnerID INT NOT NULL, -- Ⱥ�������ߵ��û�ID
    CreatedAt DATETIME DEFAULT GETDATE(), -- ����ʱ�䣬Ĭ�ϵ�ǰʱ��
    Description NVARCHAR(MAX), -- Ⱥ������
    CONSTRAINT FK_Group_Owner FOREIGN KEY (OwnerID) REFERENCES Users(UserID)
);

-- ����Ⱥ���Ա��
CREATE TABLE GroupMembers (
    GroupMemberID INT IDENTITY(1,1) PRIMARY KEY, -- �Զ�����������
    GroupID INT NOT NULL, -- Ⱥ��ID
    MemberID INT NOT NULL, -- ��ԱID
    JoinedAt DATETIME DEFAULT GETDATE(), -- ����ʱ�䣬Ĭ�ϵ�ǰʱ��
    IsAdmin BIT DEFAULT 0, -- �Ƿ�Ϊ����Ա��Ĭ�ϲ���
    CONSTRAINT FK_GroupMember_Group FOREIGN KEY (GroupID) REFERENCES Groups(GroupID),
    CONSTRAINT FK_GroupMember_User FOREIGN KEY (MemberID) REFERENCES Users(UserID),
    CONSTRAINT UQ_GroupMember_UniquePair UNIQUE (GroupID, MemberID) -- ȷ��һ��Ⱥ���еĳ�ԱΨһ
);

CREATE TABLE GroupMessages (
    GroupMessageID BIGINT IDENTITY(1,1) PRIMARY KEY, -- �Զ������Ĵ���������
    GroupID INT NOT NULL, -- Ⱥ��ID
    SenderID INT NOT NULL, -- ������ID
    Content NVARCHAR(MAX) NOT NULL, -- ��Ϣ����
    SentAt DATETIME DEFAULT GETDATE(), -- ����ʱ�䣬Ĭ�ϵ�ǰʱ��
    IsRead BIT DEFAULT 0, -- �Ƿ��Ѷ���Ĭ��δ��
    CONSTRAINT FK_GroupMessage_Group FOREIGN KEY (GroupID) REFERENCES Groups(GroupID),
    CONSTRAINT FK_GroupMessage_Sender FOREIGN KEY (SenderID) REFERENCES Users(UserID)
);

CREATE TABLE GroupRequests (
    GroupRequestID INT IDENTITY(1,1) PRIMARY KEY,
    GroupID INT NOT NULL,
    UserID INT NOT NULL,
    Status_ NVARCHAR(20) NOT NULL CHECK (Status_ IN ('Pending', 'Accepted', 'Rejected')), -- ��ϵ״̬
    CreatedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_GroupRequests_Group FOREIGN KEY (GroupID) REFERENCES Groups(GroupID),
    CONSTRAINT FK_GroupRequests_User FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- ����������Ż���ѯ����
CREATE INDEX IX_Groups_Name ON Groups(GroupName);
CREATE INDEX IX_GroupMembers_GroupID ON GroupMembers(GroupID);
CREATE INDEX IX_GroupMembers_MemberID ON GroupMembers(MemberID);
CREATE INDEX IX_GroupMessages_GroupID ON GroupMessages(GroupID);
CREATE INDEX IX_GroupMessages_SenderID ON GroupMessages(SenderID);
CREATE INDEX IX_GroupMessages_SentAt ON GroupMessages(SentAt);