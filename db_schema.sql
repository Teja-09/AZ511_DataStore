use az511;

CREATE TABLE cameras (
    id INT PRIMARY KEY,
    source VARCHAR(10),
    roadway VARCHAR(10),
    direction VARCHAR(50),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location VARCHAR(50)
);

CREATE TABLE camera_views (
    id INT PRIMARY KEY,
    camera_id INT,
    url VARCHAR(100),
    status VARCHAR(10),
    description TEXT,
    FOREIGN KEY (camera_id) REFERENCES cameras(id)
);

CREATE TABLE weather_stations (
    id INT PRIMARY KEY,
    camera_id INT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    air_temperature DECIMAL(5, 2),
    surface_temperature DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    wind_direction VARCHAR(10),
    relative_humidity INT,
    level_of_grip VARCHAR(50),
    max_wind_speed DECIMAL(5, 2),
    last_updated DATETIME,
    FOREIGN KEY (camera_id) REFERENCES cameras(id)
);
select * from weather_stations;

-- Indexing foreign key optimizes joins
CREATE INDEX idx_camera_views_camera_id ON camera_views(camera_id);
CREATE INDEX idx_weather_stations_camera_id ON weather_stations(camera_id);


CREATE TABLE weather_stations_archive (
	archive_id INT AUTO_INCREMENT PRIMARY KEY,
    original_id INT,
    camera_id INT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    air_temperature DECIMAL(5, 2),
    surface_temperature DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    wind_direction VARCHAR(10),
    relative_humidity INT,
    level_of_grip VARCHAR(50),
    max_wind_speed DECIMAL(5, 2),
    last_updated DATETIME,
	FOREIGN KEY (original_id) REFERENCES weather_stations(id)
);
-- drop table weather_stations_archive;
select * from weather_stations_archive;