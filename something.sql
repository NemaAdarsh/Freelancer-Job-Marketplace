CREATE TABLE client (
    client_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(15),
    company_name VARCHAR(255),
    posted_jobs INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (client_id)
);

CREATE TABLE freelancer (
    freelancer_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(15),
    skills TEXT,
    rating DECIMAL(3,2),
    is_available TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (freelancer_id)
);

CREATE TABLE jobs (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    budget DECIMAL(10,2) NOT NULL,
    deadline DATE NOT NULL,
    description TEXT,
    status ENUM('Open', 'Closed') DEFAULT 'Open',
    category VARCHAR(100),
    required_skills TEXT,
    client_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
);

CREATE TABLE proposals (
    id INT NOT NULL AUTO_INCREMENT,
    job_id INT NOT NULL,
    cover_letter TEXT,
    proposed_rate DECIMAL(10,2),
    estimated_time INT,
    freelancer_id INT NOT NULL,
    status ENUM('Pending', 'Accepted', 'Rejected') DEFAULT 'Pending',
    PRIMARY KEY (id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (freelancer_id) REFERENCES freelancer(freelancer_id) ON DELETE CASCADE
);

CREATE TABLE contracts (
    id INT NOT NULL AUTO_INCREMENT,
    job_id INT NOT NULL,
    freelancer_id INT NOT NULL,
    payment DECIMAL(10,2),
    status ENUM('In Progress', 'Completed') DEFAULT 'In Progress',
    PRIMARY KEY (id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (freelancer_id) REFERENCES freelancer(freelancer_id) ON DELETE SET NULL
);

CREATE TABLE ratings (
    rating_id INT NOT NULL AUTO_INCREMENT,
    contract_id INT NOT NULL,
    rating_score INT,
    review_text TEXT,
    rating_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (rating_id),
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);



DELIMITER //

CREATE PROCEDURE accept_proposal(
    IN proposal_id_param INT,
    OUT status_message VARCHAR(100)
)
BEGIN
    DECLARE v_job_id INT;
    DECLARE v_freelancer_id INT;
    DECLARE v_proposed_rate DECIMAL(10,2);
    DECLARE v_job_status VARCHAR(10);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET status_message = 'Error occurred. Operation rolled back.';
    END;
    
    START TRANSACTION;
    
    SELECT job_id, freelancer_id, proposed_rate 
    INTO v_job_id, v_freelancer_id, v_proposed_rate
    FROM proposals 
    WHERE id = proposal_id_param;
    
    SELECT status INTO v_job_status 
    FROM jobs 
    WHERE id = v_job_id;
    
    IF v_job_status = 'Closed' THEN
        SET status_message = 'Job is already closed';
        ROLLBACK;
    ELSE
        UPDATE proposals 
        SET status = 'Accepted' 
        WHERE id = proposal_id_param;
        
        UPDATE proposals 
        SET status = 'Rejected' 
        WHERE job_id = v_job_id 
        AND id != proposal_id_param;
        
        INSERT INTO contracts (job_id, freelancer_id, payment, status)
        VALUES (v_job_id, v_freelancer_id, v_proposed_rate, 'In Progress');
        
        UPDATE jobs 
        SET status = 'Closed' 
        WHERE id = v_job_id;
        
        COMMIT;
        SET status_message = 'Proposal accepted and contract created successfully';
    END IF;
END //

CREATE FUNCTION calculate_freelancer_rating(freelancer_id_param INT)
RETURNS DECIMAL(3,2)
READS SQL DATA
BEGIN
    DECLARE avg_rating DECIMAL(3,2);
    
    SELECT COALESCE(AVG(r.rating_score), 0.00) INTO avg_rating
    FROM ratings r
    JOIN contracts c ON r.contract_id = c.id
    WHERE c.freelancer_id = freelancer_id_param
    AND c.status = 'Completed';
    
    RETURN avg_rating;
END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER BeforeInsertRating
BEFORE INSERT ON ratings
FOR EACH ROW
BEGIN
    DECLARE contractStatus ENUM('In Progress', 'Completed');

    SELECT status INTO contractStatus
    FROM contracts
    WHERE id = NEW.contract_id;

    IF contractStatus != 'Completed' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Contract must be completed before rating.';
    END IF;
END //

DELIMITER ;


