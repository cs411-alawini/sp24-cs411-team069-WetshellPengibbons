SELECT
    d.DepartmentName,
    ROUND(AVG(
            IF(
                ag.NumberAPlus + ag.NumberA + ag.NumberAMinus +
                ag.NumberBPlus + ag.NumberB + ag.NumberBMinus +
                ag.NumberCPlus + ag.NumberC + ag.NumberCMinus +
                ag.NumberDPlus + ag.NumberD + ag.NumberDMinus +
                ag.NumberF = 0,
                NULL,
                (ag.NumberAPlus * 4.0 + ag.NumberA * 4.0 + ag.NumberAMinus * 3.67 +
                ag.NumberBPlus * 3.33 + ag.NumberB * 3.0 + ag.NumberBMinus * 2.67 +
                ag.NumberCPlus * 2.33 + ag.NumberC * 2.0 + ag.NumberCMinus * 1.67 +
                ag.NumberDPlus * 1.33 + ag.NumberD * 1.0 + ag.NumberDMinus * 0.67 +
                ag.NumberF * 0) /
                (ag.NumberAPlus + ag.NumberA + ag.NumberAMinus +
                ag.NumberBPlus + ag.NumberB + ag.NumberBMinus +
                ag.NumberCPlus + ag.NumberC + ag.NumberCMinus +
                ag.NumberDPlus + ag.NumberD + ag.NumberDMinus +
                ag.NumberF)
            )
        ), 2) AS AvgGPA
FROM Department d
LEFT JOIN CourseInfo ci ON d.DepartmentName = ci.DepartmentName
LEFT JOIN AverageGPA ag ON ci.CourseCode = ag.CourseCode
GROUP BY d.DepartmentName
ORDER BY AvgGPA DESC;