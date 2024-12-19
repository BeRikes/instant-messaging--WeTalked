USE InstantMessagingDB;
GO

-- 创建用户表
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY, -- 自动递增的主键
    Username NVARCHAR(50) NOT NULL UNIQUE, -- 用户名，不允许重复
    PasswordHash VARBINARY(64) NOT NULL, -- 哈希后的密码
    Email NVARCHAR(100) NOT NULL UNIQUE, -- 电子邮件地址，不允许重复
    PhoneNumber NVARCHAR(20), -- 可选的电话号码
    CreatedAt DATETIME DEFAULT GETDATE(), -- 创建时间，默认当前时间
    LastLogin DATETIME, -- 最后登录时间
    IsActive BIT DEFAULT 1 -- 账户是否激活，默认激活
);

-- 创建好友关系表
CREATE TABLE Friendships (
    FriendshipID INT IDENTITY(1,1) PRIMARY KEY, -- 自动递增的主键
    User1ID INT NOT NULL, -- 第一个用户ID
    User2ID INT NOT NULL, -- 第二个用户ID
    Status_ NVARCHAR(20) NOT NULL CHECK (Status_ IN ('Pending', 'Accepted', 'Rejected')), -- 关系状态
    CreatedAt DATETIME DEFAULT GETDATE(), -- 创建时间，默认当前时间
    CONSTRAINT FK_Friendship_User1 FOREIGN KEY (User1ID) REFERENCES Users(UserID),
    CONSTRAINT FK_Friendship_User2 FOREIGN KEY (User2ID) REFERENCES Users(UserID),
    CONSTRAINT CHK_Friendship_DistinctUsers CHECK (User1ID <> User2ID), -- 确保两个用户不是同一个
    CONSTRAINT UQ_Friendship_UniquePair UNIQUE (User1ID, User2ID) -- 确保一对用户之间的关系唯一
);

-- 创建消息表
CREATE TABLE Messages_ (
    MessageID BIGINT IDENTITY(1,1) PRIMARY KEY, -- 自动递增的大整数主键
    SenderID INT NOT NULL, -- 发送者ID
    ReceiverID INT NOT NULL, -- 接收者ID
    Content NVARCHAR(MAX) NOT NULL, -- 消息内容
    SentAt DATETIME DEFAULT GETDATE(), -- 发送时间，默认当前时间
    IsRead BIT DEFAULT 0, -- 是否已读，默认未读
    CONSTRAINT FK_Message_Sender FOREIGN KEY (SenderID) REFERENCES Users(UserID),
    CONSTRAINT FK_Message_Receiver FOREIGN KEY (ReceiverID) REFERENCES Users(UserID)
);

-- 添加索引以优化查询性能
-- 对于用户表，通常我们会对经常查询的字段建立索引
CREATE INDEX IX_Users_Username ON Users(Username);
CREATE INDEX IX_Users_Email ON Users(Email);

-- 对于好友关系表，确保快速查找特定用户的联系人列表
CREATE INDEX IX_Friendships_User1ID ON Friendships(User1ID);
CREATE INDEX IX_Friendships_User2ID ON Friendships(User2ID);

-- 对于消息表，优化根据发送者、接收者以及发送时间的查询
CREATE INDEX IX_Messages_SenderID ON Messages_(SenderID);
CREATE INDEX IX_Messages_ReceiverID ON Messages_(ReceiverID);
CREATE INDEX IX_Messages_SentAt ON Messages_(SentAt);
CREATE INDEX IX_Messages_IsRead ON Messages_(IsRead);

-- 如果需要频繁地按照发送者和接收者的组合进行查询，可以创建复合索引
CREATE INDEX IX_Messages_SenderID_ReceiverID ON Messages_(SenderID, ReceiverID);

-- 创建群组表
CREATE TABLE Groups (
    GroupID INT IDENTITY(1,1) PRIMARY KEY, -- 自动递增的主键
    GroupName NVARCHAR(100) NOT NULL, -- 群组名称
    OwnerID INT NOT NULL, -- 群组所有者的用户ID
    CreatedAt DATETIME DEFAULT GETDATE(), -- 创建时间，默认当前时间
    Description NVARCHAR(MAX), -- 群组描述
    CONSTRAINT FK_Group_Owner FOREIGN KEY (OwnerID) REFERENCES Users(UserID)
);

-- 创建群组成员表
CREATE TABLE GroupMembers (
    GroupMemberID INT IDENTITY(1,1) PRIMARY KEY, -- 自动递增的主键
    GroupID INT NOT NULL, -- 群组ID
    MemberID INT NOT NULL, -- 成员ID
    JoinedAt DATETIME DEFAULT GETDATE(), -- 加入时间，默认当前时间
    IsAdmin BIT DEFAULT 0, -- 是否为管理员，默认不是
    CONSTRAINT FK_GroupMember_Group FOREIGN KEY (GroupID) REFERENCES Groups(GroupID),
    CONSTRAINT FK_GroupMember_User FOREIGN KEY (MemberID) REFERENCES Users(UserID),
    CONSTRAINT UQ_GroupMember_UniquePair UNIQUE (GroupID, MemberID) -- 确保一个群组中的成员唯一
);

CREATE TABLE GroupMessages (
    GroupMessageID BIGINT IDENTITY(1,1) PRIMARY KEY, -- 自动递增的大整数主键
    GroupID INT NOT NULL, -- 群组ID
    SenderID INT NOT NULL, -- 发送者ID
    Content NVARCHAR(MAX) NOT NULL, -- 消息内容
    SentAt DATETIME DEFAULT GETDATE(), -- 发送时间，默认当前时间
    IsRead BIT DEFAULT 0, -- 是否已读，默认未读
    CONSTRAINT FK_GroupMessage_Group FOREIGN KEY (GroupID) REFERENCES Groups(GroupID),
    CONSTRAINT FK_GroupMessage_Sender FOREIGN KEY (SenderID) REFERENCES Users(UserID)
);

CREATE TABLE GroupRequests (
    GroupRequestID INT IDENTITY(1,1) PRIMARY KEY,
    GroupID INT NOT NULL,
    UserID INT NOT NULL,
    Status_ NVARCHAR(20) NOT NULL CHECK (Status_ IN ('Pending', 'Accepted', 'Rejected')), -- 关系状态
    CreatedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_GroupRequests_Group FOREIGN KEY (GroupID) REFERENCES Groups(GroupID),
    CONSTRAINT FK_GroupRequests_User FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- 添加索引以优化查询性能
CREATE INDEX IX_Groups_Name ON Groups(GroupName);
CREATE INDEX IX_GroupMembers_GroupID ON GroupMembers(GroupID);
CREATE INDEX IX_GroupMembers_MemberID ON GroupMembers(MemberID);
CREATE INDEX IX_GroupMessages_GroupID ON GroupMessages(GroupID);
CREATE INDEX IX_GroupMessages_SenderID ON GroupMessages(SenderID);
CREATE INDEX IX_GroupMessages_SentAt ON GroupMessages(SentAt);