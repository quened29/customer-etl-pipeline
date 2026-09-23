-- What is the current size of our customer base?

SELECT COUNT(*) AS total_customers
FROM customers;

-- Which age groups represent the largest share of our customer base?

SELECT
    age_range,
    COUNT(*) AS customer_count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS customer_percentage
FROM customers
GROUP BY age_range
ORDER BY customer_count DESC;

-- What is the average age of our customers?

SELECT
    ROUND(AVG(CAST(age AS FLOAT)), 1) AS average_customer_age (que hace el cast aqui?)
FROM customers
WHERE age IS NOT NULL;

-- How long have our customers been registered with the company on average?

SELECT
    ROUND(AVG(CAST(customer_tenure AS FLOAT)), 1) AS average_customer_tenure
FROM customers
WHERE customer_tenure IS NOT NULL;

-- What percentage of our customer base has an invalid email address?

SELECT
    COUNT(*) AS invalid_email_count,
    ROUND(
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers),
        2
    ) AS invalid_email_rate
FROM customers
WHERE email_valid = 0;

-- Does customer tenure vary across different age groups?

SELECT
    age_range,
    COUNT(*) AS customer_count,
    ROUND(AVG(CAST(customer_tenure AS FLOAT)), 1) AS average_tenure
FROM customers
WHERE customer_tenure IS NOT NULL
GROUP BY age_range
ORDER BY average_tenure DESC;

-- How has customer acquisition evolved over time?

SELECT
    YEAR(registration_date) AS registration_year,
    COUNT(*) AS new_customers
FROM customers
GROUP BY YEAR(registration_date)
ORDER BY registration_year;

-- What proportion of our customer base consists of new versus long-term customers?

SELECT
    CASE
        WHEN customer_tenure < 1 THEN 'Less than 1 year'
        WHEN customer_tenure BETWEEN 1 AND 3 THEN '1-3 years'
        WHEN customer_tenure BETWEEN 4 AND 6 THEN '4-6 years'
        ELSE '7+ years'
    END AS tenure_group,
    COUNT(*) AS customer_count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS customer_percentage
FROM customers
GROUP BY
    CASE
        WHEN customer_tenure < 1 THEN 'Less than 1 year'
        WHEN customer_tenure BETWEEN 1 AND 3 THEN '1-3 years'
        WHEN customer_tenure BETWEEN 4 AND 6 THEN '4-6 years'
        ELSE '7+ years'
    END
ORDER BY customer_count DESC;