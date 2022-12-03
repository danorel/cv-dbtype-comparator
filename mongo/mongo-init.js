db.createUser(
        {
            user: "mongo",
            pwd: "supersecretpassword",
            roles: [
                {
                    role: "readWrite",
                    db: "test"
                }
            ]
        }
);