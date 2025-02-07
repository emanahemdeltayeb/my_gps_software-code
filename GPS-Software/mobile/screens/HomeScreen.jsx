import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Image, TouchableOpacity, Easing } from 'react-native';
import MapView, { AnimatedRegion, Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import * as Location from 'expo-location';
import { MaterialIcons } from '@expo/vector-icons';

const demoCoords = [
  [25.3868954, 55.4680188],
  [25.3858584, 55.4669348],
  [25.3851797, 55.4662947],
  [25.3843016, 55.4654339],
  [25.3832625, 55.4645236],
  [25.3822023, 55.4634995],
  [25.381237, 55.4626671],
  [25.380043, 55.4615147],
  [25.3783453, 55.4599849],
  [25.3766098, 55.4583887],
  [25.3747417, 55.4565681],
  [25.3735681, 55.4552365],
  [25.3728745, 55.4546077],
  [25.372460, 55.454076],
  [25.372374, 55.453602],
  [25.372553, 55.453199],
  [25.372884, 55.453006],
  [25.373445, 55.453181],
  [25.373424, 55.454274],
  [25.372856, 55.455093],
  [25.372383, 55.455779],
];

const demoCoordsReverse = [...demoCoords].reverse();

const calculateDirectionDistance = (current, previous) => {
  const [lat1, lon1] = previous;
  const [lat2, lon2] = current;

  const toRadians = (deg) => deg * (Math.PI / 180);

  const radLat1 = toRadians(lat1);
  const radLat2 = toRadians(lat2);
  const deltaLat = toRadians(lat2 - lat1);
  const deltaLon = toRadians(lon2 - lon1);

  const y = Math.sin(deltaLon) * Math.cos(radLat2);
  const x =
    Math.cos(radLat1) * Math.sin(radLat2) -
    Math.sin(radLat1) * Math.cos(radLat2) * Math.cos(deltaLon);

  const bearing = Math.atan2(y, x);
  const bearingDegrees = (bearing * (180 / Math.PI) + 360) % 360;

  const earthRadiusKm = 6371;
  const a =
    Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
    Math.cos(radLat1) * Math.cos(radLat2) *
      Math.sin(deltaLon / 2) * Math.sin(deltaLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distanceKm = earthRadiusKm * c;

  return {
    direction: bearingDegrees,
    distance: distanceKm,
  };
};

const HomeScreen = () => {
  const [cars, setCars] = useState([
    {
      label: "Employee's Car",
      currentCoords: new AnimatedRegion({
        latitude: demoCoords[0][0],
        longitude: demoCoords[0][1],
        latitudeDelta: 0.01,
        longitudeDelta: 0.01,
      }),
      counter: 0,
      demoList: demoCoords,
      icon: {
        source: require('../assets/car.png'),
        dimensions: [32, 60],
      },
    },
    {
      label: "New Truck",
      currentCoords: new AnimatedRegion({
        latitude: demoCoordsReverse[0][0],
        longitude: demoCoordsReverse[0][1],
        latitudeDelta: 0.01,
        longitudeDelta: 0.01,
      }),
      counter: 0,
      demoList: demoCoordsReverse,
      icon: {
        source: require('../assets/truck.png'),
        dimensions: [60, 60],
      },
    },
  ]);
  const mapRef = React.useRef();
  const [cameraHeading, setCameraHeading] = useState(0);
  const [mapType, setMapType] = useState('standard');
  const [showTraffic, setShowTraffic] = useState(false);

  function updateCameraHeading() {
    const map = mapRef.current;
    map.getCamera().then((info) => {
      setCameraHeading(info.heading);
    });
  }

  useEffect(() => {
    const interval = setInterval(() => {
      setCars((prevCars) =>
        prevCars.map((car) => {
          const { counter, demoList } = car;
          const nextCounter = counter + 1 < demoList.length ? counter + 1 : 0;

          const directionDistance = calculateDirectionDistance(
            demoList[nextCounter],
            demoList[counter]
          );

          car.currentCoords.timing({
            latitude: demoList[nextCounter][0],
            longitude: demoList[nextCounter][1],
            duration: 2000, // Match the interval duration
            useNativeDriver: false, // Required for smooth animation
            easing: Easing.linear,
          }).start();

          return {
            ...car,
            counter: nextCounter,
            speed: ((directionDistance.distance / 2) * 1000).toFixed(2), // Speed in km/h
            direction: directionDistance.direction,
          };
        })
      );
      updateCameraHeading();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const goToMyLocation = async () => {
    let { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      return;
    }

    let location = await Location.getCurrentPositionAsync({});
    mapRef.current.animateToRegion({
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
      latitudeDelta: 0.01,
      longitudeDelta: 0.01,
    });
  };

  const toggleSatelliteMode = () => {
    setMapType(mapType === 'standard' ? 'hybrid' : 'standard');
  };

  const toggleTrafficMode = () => {
    setShowTraffic(!showTraffic);
  };

  return (
    <View style={styles.container}>
      <MapView
        ref={mapRef}
        style={styles.map}
        showsUserLocation={true}
        // provider={PROVIDER_GOOGLE}
        mapType={mapType}
        showsTraffic={showTraffic}
        initialRegion={{
          latitude: 25.3750097,
          longitude: 55.4573421,
          latitudeDelta: 0.01,
          longitudeDelta: 0.01,
        }}
      >
        {cars.map((car, index) => (
          <Marker.Animated
            key={index}
            coordinate={car.currentCoords}
            anchor={{ x: 0.5, y: 0.5 }}
            title={car.label}
            description={`Speed: ${car.speed} km/h`}
          >
            <Image
              source={car.icon.source}
              style={{ width: car.icon.dimensions[0], height: car.icon.dimensions[1], transform: [{ rotate: `${car.direction - cameraHeading}deg`} ] }}
              resizeMode="contain"
            />
          </Marker.Animated>      
        ))}
      </MapView>
      <TouchableOpacity style={styles.locationButton} onPress={goToMyLocation}>
        <MaterialIcons name="my-location" size={24} color="black" />
      </TouchableOpacity>
      <View style={styles.topRightButtons}>
        <TouchableOpacity style={styles.button} onPress={toggleSatelliteMode}>
          <MaterialIcons name="satellite" size={24} color="black" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={toggleTrafficMode}>
          <MaterialIcons name="traffic" size={24} color="black" />
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    ...StyleSheet.absoluteFillObject,
  },
  locationButton: {
    position: 'absolute',
    bottom: 16,
    left: 16,
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 30,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  topRightButtons: {
    position: 'absolute',
    top: 16,
    right: 16,
    flexDirection: 'column',
  },
  button: {
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 30,
    marginBottom: 10,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
});

export default HomeScreen;

