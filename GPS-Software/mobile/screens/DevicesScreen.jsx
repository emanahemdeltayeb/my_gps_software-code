import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Dimensions, Platform, TouchableOpacity } from 'react-native';
import { widthPercentageToDP as wp } from 'react-native-responsive-screen';
import { Searchbar, Chip } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import AntDesign from '@expo/vector-icons/AntDesign';

import MobileDeviceList from '../components/MobileDeviceList';

const DevicesScreen = () => {
  const [isDesktop, setIsDesktop] = useState(Dimensions.get('window').width >= 768);
  const [searchQuery, setSearchQuery] = useState('');
  const [devices, setDevices] = useState([]);
  const [filters, setFilters] = useState({
    status: '',
    model: '',
  });
  const navigation = useNavigation();

  useEffect(() => {
    const updateLayout = () => {
      setIsDesktop(Dimensions.get('window').width >= 768);
    };

    Dimensions.addEventListener('change', updateLayout);
    return () => {
      Dimensions.removeEventListener('change', updateLayout);
    };
  }, []);

  useEffect(() => {
    setDevices([
      { id: '1', name: 'Device 1', deviceId: 'DEV001', model: 'Model A', importTime: '2023-05-01', status: 'Active', user: 'user1' },
      { id: '2', name: 'Device 2', deviceId: 'DEV002', model: 'Model B', importTime: '2023-05-02', status: 'Inactive', user: 'user1' },
      { id: '3', name: 'Device 3', deviceId: 'DEV003', model: 'Model A', importTime: '2023-05-03', status: 'Active', user: 'user1' },
      { id: '4', name: 'Device 4', deviceId: 'DEV004', model: 'Model C', importTime: '2023-05-04', status: 'Inactive', user: 'user2' },
    ]);
  }, []);

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const handleFilter = (key, value) => {
    setFilters(prevFilters => ({
      ...prevFilters,
      [key]: prevFilters[key] === value ? '' : value
    }));
  };

  const filteredDevices = devices.filter(device => {
    return (
      (filters.status === '' || device.status === filters.status) &&
      (filters.model === '' || device.model === filters.model) &&
      (device.name.toLowerCase().includes(searchQuery.toLowerCase()) || device.model.toLowerCase().includes(searchQuery.toLowerCase()) || device.user.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  });

  return (
    <View style={styles.container}>
      {!isDesktop &&
      <TouchableOpacity
            style={styles.addButton}
            onPress={() => { navigation.navigate('Add Device') }}
      ><AntDesign name="plus" size={40} color="white" /></TouchableOpacity>
      }
      <Searchbar
        placeholder="Search devices"
        onChangeText={handleSearch}
        value={searchQuery}
        style={styles.searchBar}
      />
      <View style={styles.filterContainer}>
        <Chip
          selected={filters.status === 'Active'}
          onPress={() => handleFilter('status', 'Active')}
          style={styles.filterChip}
        >
          Active
        </Chip>
        <Chip
          selected={filters.status === 'Inactive'}
          onPress={() => handleFilter('status', 'Inactive')}
          style={styles.filterChip}
        >
          Inactive
        </Chip>
        <Chip
          selected={filters.model === 'Model A'}
          onPress={() => handleFilter('model', 'Model A')}
          style={styles.filterChip}
        >
          Model A
        </Chip>
        <Chip
          selected={filters.model === 'Model B'}
          onPress={() => handleFilter('model', 'Model B')}
          style={styles.filterChip}
        >
          Model B
        </Chip>
        <Chip
          selected={filters.model === 'Model C'}
          onPress={() => handleFilter('model', 'Model C')}
          style={styles.filterChip}
        >
          Model C
        </Chip>
      </View>
      <MobileDeviceList devices={filteredDevices} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: wp('2%'),
    backgroundColor: '#f5f5f5',
  },
  searchBar: {
    marginBottom: 10,
    elevation: 2,
  },
  filterContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: wp('2%'),
    justifyContent: Platform.OS === 'web' ? 'start' : 'center'
  },
  filterChip: {
    marginRight: wp('1%'),
    marginBottom: wp('1%'),
  },
  addButton: {
    borderWidth: 1,
    borderColor: '#4594f1',
    alignItems: 'center',
    justifyContent: 'center',
    width: 60,
    height: 60,
    position: 'absolute',
    bottom: 10,
    end: 15,
    backgroundColor: '#4594f1',
    borderRadius: 100,
    zIndex: 1,
  }
});

export default DevicesScreen;
