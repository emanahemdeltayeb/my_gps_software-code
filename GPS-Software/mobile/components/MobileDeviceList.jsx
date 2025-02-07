import React, { useMemo } from 'react';
import { View, Text, StyleSheet, SectionList, TouchableOpacity } from 'react-native';
import { List, Avatar } from 'react-native-paper';
import { widthPercentageToDP as wp } from 'react-native-responsive-screen';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const MobileDeviceList = ({ devices }) => {
  const sections = useMemo(() => {
    const groupedDevices = devices.reduce((acc, device) => {
      if (!acc[device.user]) {
        acc[device.user] = [];
      }
      acc[device.user].push(device);
      return acc;
    }, {});

    return Object.entries(groupedDevices).map(([user, data]) => ({
      title: user,
      data,
    }));
  }, [devices]);

  const renderItem = ({ item }) => (
    <TouchableOpacity onPress={() => console.log('Device pressed:', item.id)}>
      <List.Item
        title={item.name}
        description={item.deviceId}
        left={() => <Avatar.Icon color="white" size={40} icon="devices" />}
        right={() => (
          <View style={styles.rightContent}>
            <View style={[styles.statusIndicator, { backgroundColor: item.status === 'Active' ? 'green' : 'red' }]} />
            <Icon name="chevron-right" size={24} color="#000" />
          </View>
        )}
        style={styles.listItem}
      />
    </TouchableOpacity>
  );

  const renderSectionHeader = ({ section: { title } }) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionHeaderText}>{title}</Text>
    </View>
  );

  return (
    <SectionList
      sections={sections}
      renderItem={renderItem}
      renderSectionHeader={renderSectionHeader}
      keyExtractor={(item) => item.id}
      contentContainerStyle={styles.listContainer}
    />
  );
};

const styles = StyleSheet.create({
  listContainer: {
    paddingVertical: wp('2%'),
  },
  listItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    paddingRight: wp('2%'),
  },
  rightContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: wp('2%'),
  },
  sectionHeader: {
    backgroundColor: '#f0f0f0',
    padding: wp('2%'),
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  sectionHeaderText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default MobileDeviceList;

